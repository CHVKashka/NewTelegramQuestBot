import sqlite3
import threading
from contextlib import contextmanager
from typing import Iterator

from utils import log


class SQLiteDatabase:
    def __init__(self, db_path: str = "data.SQLITE3", timeout: float = 10.0):
        self.db_path = db_path
        self.timeout = timeout
        self.local = threading.local()
        self.initialize_database()

    def initialize_database(self) -> None:
        """Создает таблицы пользователей и сообщений, если они не существуют"""
        with self.connection() as cursor:
            # Таблица пользователей с колонками ключ-значение
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Users (
                    user_id INTEGER NOT NULL,
                    username TEXT NOT NULL,
                    session_id INTEGER,
                    opened_menu TEXT NOT NULL,
                    menu_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id)
            )""")

            # Таблица сообщений
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Messages (
                    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL
            )""")
            cursor.execute("""
                   CREATE TABLE IF NOT EXISTS Sessions (
                       session_id INTEGER PRIMARY KEY,
                       session_code TEXT NOT NULL,
                       reg_requier INTEGER DEFAULT 0,
                       allow_team INTEGER DEFAULT 0
               )""")

            # Включаем WAL режим для конкурентного доступа
            cursor.execute("PRAGMA journal_mode=WAL;")

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Cursor]:
        """Контекстный менеджер для безопасного подключения"""
        if not hasattr(self.local, "conn"):
            self.local.conn = sqlite3.connect(
                self.db_path,
                timeout=self.timeout,
                check_same_thread=False
            )
            self.local.conn.row_factory = sqlite3.Row

        cursor = self.local.conn.cursor()
        try:
            yield cursor
            self.local.conn.commit()
        except Exception as e:
            self.local.conn.rollback()
            raise e

    def addUser(self, user_id, username,menu_id):
        try:
            with self.connection() as cursor:
                cursor.execute(
                    f'INSERT INTO Users (user_id,username,session_id,opened_menu,menu_id) VALUES (?,?,?,?,?)',
                    (user_id, username, 0,'start',menu_id))
        except Exception as error:
            if "UNIQUE" in str(error):
                log(f'Ошибка добавления пользователя {user_id}: пользователь уже существует', 'Database', 'strong')
            else:
                print(error)
                log(f'Ошибка добавления пользователя {user_id}: {error}', 'Database', 'error')

    def updateUser(self, user_id, data):
        try:
            with self.connection() as cursor:
                cursor.execute(f'SELECT 1 FROM Users WHERE user_id = ?', (user_id,))
                exists = cursor.fetchone()

                if exists:
                    for key, val in data.items():
                        cursor.execute(f"UPDATE Users SET {key} = ? WHERE user_id=?", (val, user_id))
                else:
                    log(f'Пользователя {user_id} не существует', 'Database', 'strong')
        except Exception as error:
            raise error
            log(f'Ошибка обновления данных пользователя {user_id}: {error}', 'Database', 'error')

    def getUser(self, user_id=None):
        if user_id:
            with self.connection() as cursor:
                cursor.execute('SELECT * FROM Users WHERE user_id = ?', (user_id,))
                return [dict(row) for row in cursor.fetchall()]
        else:
            with (self.connection() as cursor):
                cursor.execute('SELECT * FROM Users')
                return [dict(row) for row in cursor.fetchall()]

    def addMessage(self, message_id, user_id):
        with self.connection() as cursor:
            try:
                cursor.execute('INSERT INTO Messages (message_id,user_id) VALUES (?,?)', (message_id, user_id))
            except Exception as error:
                log(f'Ошибка {error} при добавлении сообщения {message_id} к {user_id}', 'Database', 'error')

    def getMessages(self, user_id=None):
        try:
            with self.connection() as cursor:
                if user_id:
                    cursor.execute(f'SELECT 1 FROM Messages WHERE message_id = ?', (user_id,))
                    return cursor.fetchone()
                else:
                    cursor.execute(f'SELECT * FROM Messages WHERE message_id = ?', (user_id,))
                    return cursor.fetchall()
        except Exception as error:
            log(f'Ошибка {error} при получении сообщений пользователем {user_id}', 'Database', 'error')
            return None

    def removeMessages(self, user_id, message_id=None):
        try:
            with self.connection() as cursor:
                if message_id:
                    cursor.execute(f"DELETE FROM Messages WHERE {user_id}=?,{message_id}=?", (user_id, message_id))
                else:
                    cursor.execute(f"DELETE FROM Messages WHERE {user_id}=?", (user_id,))
        except Exception as error:
            log(f'Ошибка {error} при удаления сообщений пользователем {user_id}', 'Database', 'error')

    def createSession(self, session_id, session_code, user_id, username):
        with self.connection() as cursor:
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS Session_{session_id} (
                   user_id INTEGER PRIMARY KEY NOT NULL,
                   username TEXT NOT NULL,
                   team TEXT,
                   complite TEXT,
                   score INTEGER NOT NULL,
                   is_admin INTEGER NOT NULL
               )
           """)
            cursor.execute(
                f"INSERT INTO Session_{session_id} (user_id,username,score,is_admin) VALUES (?,?,?,?)",
                (user_id, username, 0, 2))
            cursor.execute(f"INSERT INTO Sessions (session_id,session_code) VALUES (?,?)",
                           (session_id, session_code))
            self.updateUser(user_id, {"session_id": session_id})

    def joinSession(self,session_id,user_id,username):
        with self.connection() as cursor:
            try:
                cursor.execute(
                    f"INSERT INTO Session_{session_id} (user_id,username,score,is_admin) VALUES (?,?,?,?)",
                    (user_id, username, 0, 0))
                return 0
            except Exception as error:
                log(f'Ошибка {error} при присоединении к сессии {session_id}', 'Database', 'error')
                return 1

    def leaveSession(self,session_id,user_id):
        with self.connection() as cursor:
            try:
                cursor.execute(f"DELETE FROM Session_{session_id} WHERE user_id=?",(user_id,))
                self.updateUser(user_id,{'session_id':0})
                #cursor.execute(f"DELETE FROM Messages WHERE {user_id}=?", (user_id,))
            except Exception as error:
                log(f"Ошибка выхода пользователя {user_id} из сессии {session_id}")

    def removeSession(self, session_id):
        with self.connection() as cursor:
            users = self.getSessionData(session_id)
            for user in users:
                self.updateUser(int(user["user_id"]), {"session_id": 0})
            cursor.execute(f"DELETE FROM Sessions WHERE session_id=?", (session_id,))
            sessionTable = f"Session_{session_id}"
            cursor.execute(f"DROP TABLE {sessionTable}")

    def getSessionList(self):
        with self.connection() as cursor:
            cursor.execute(f'SELECT * FROM Sessions')
            return [dict(row) for row in cursor.fetchall()]

    def getSessionData(self, session_id):
        with self.connection() as cursor:
            cursor.execute(f"SELECT * FROM Session_{session_id}")
            return [dict(row) for row in cursor.fetchall()]

    def FindInSession(self,session_id,user_id):
        with self.connection() as cursor:
            cursor.execute(f"SELECT * FROM Session_{session_id} WHERE user_id=?",(user_id,))
            return  [dict(row) for row in cursor.fetchall()][0]

