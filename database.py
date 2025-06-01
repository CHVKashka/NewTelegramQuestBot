import sqlite3
import threading
from contextlib import contextmanager
from enum import UNIQUE
from typing import Any, Dict, Iterator, List, Optional, Tuple
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
                    userid INTEGER NOT NULL,
                    username TEXT NOT NULL,
                    session INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (userid)
                )
            """)

            # Таблица сообщений
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Messages (
                    messageid INTEGER PRIMARY KEY AUTOINCREMENT,
                    userid INTEGER NOT NULL
                )
            """)
            cursor.execute("""
                   CREATE TABLE IF NOT EXISTS Sessions (
                       sessionid INTEGER PRIMARY KEY,
                       registration INTEGER DEFAULT 0,
                       data TEXT
                   )
               """)



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

    def addUser(self,userid,username):
        try:
            with self.connection() as cursor:
                cursor.execute(f'INSERT INTO Users (userid,username) VALUES (?,?)',(userid,username,))
        except Exception as error:
            if "UNIQUE" in str(error):
                log(f'Ошибка добавления пользователя {userid}: пользователь уже существует', 'Database', 'strong')
            else:
                print(error)
                log(f'Ошибка добавления пользователя {userid}: {error}', 'Database', 'error')

    def updateUser(self,userid,data):
        try:
            with self.connection() as cursor:
                cursor.execute(f'SELECT 1 FROM Users WHERE userid = ?',(userid,))
                exists=cursor.fetchone()

                if exists:
                    for key,val in data.items():
                        cursor.execute(f"UPDATE Users SET {key} = ? WHERE userid=?",(val,userid))
                else:
                    log(f'Пользователя {userid} не существует','Database','strong')
        except Exception as error:
            log(f'Ошибка обновления данных пользователя {userid}: {error}','Database','error')

    def getUser(self,userid=None):
        if userid:
            with self.connection() as cursor:
                cursor.execute('SELECT * FROM Users WHERE userid = ?',(userid,))
                return [dict(row) for row in cursor.fetchall()]
        else:
            with (self.connection() as cursor):
                cursor.execute('SELECT * FROM Users')
                return [dict(row) for row in cursor.fetchall()]

    def addMessage(self,messageid,userid):
        with self.connection() as cursor:
            try:
                cursor.execute('INSERT INTO Messages (messageid,userid) VALUES (?,?)',(messageid,userid))
            except Exception as error:
                log(f'Ошибка {error} при добавлении сообщения {messageid} к {userid}','Database','error')

    def getMessages(self,userid=None):
        try:
            with self.connection() as cursor:
                if userid:
                    cursor.execute(f'SELECT 1 FROM Messages WHERE messageid = ?', (userid,))
                    return cursor.fetchone()
                else:
                    cursor.execute(f'SELECT * FROM Messages WHERE messageid = ?', (userid,))
                    return cursor.fetchall()
        except Exception as error:
            log(f'Ошибка {error} при получении сообщений пользователем {userid}','Database','error')
            return None

    def removeMessages(self,userid,messageid=None):
        try:
            with self.connection() as cursor:
                if messageid:
                    cursor.execute(f"DELETE FROM Messages WHERE {userid}=?,{messageid}=?",(userid,messageid))
                else:
                    cursor.execute(f"DELETE FROM Messages WHERE {userid}=?", (userid,))
        except Exception as error:
            log(f'Ошибка {error} при удаления сообщений пользователем {userid}', 'Database', 'error')



    def createSession(self,sesionid):
        with self.connection() as cursor:
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS Sessions_{sesionid} (
                   userid INTEGER PRIMARY NOT NULL,
                   username TEXT NOT NULL,
                   complite TEXT NOT NULL,
                   score INTEGER NOT NULL
               )
           """)








