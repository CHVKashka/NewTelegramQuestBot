import importlib.util
import telebot
import json
import os
import signal
import sys
import time
import atexit

from utils import *
from colorama import init, Fore
from datetime import datetime as dt
from threading import Thread
from database import SQLiteDatabase
from user import UserClass


def initialize_bot():
    global bot, Data, command_handlers

    # Инициализация
    with open("settings.json", encoding='utf-8') as config_file:
        config = json.load(config_file)

    bot = telebot.TeleBot(config["system"]["token"])
    init()
    Data = SQLiteDatabase(db_path='data.SQLITE3')

    # Загрузка команд
    command_handlers = {}
    log(f'Загрузка файлов команд из {config["system"]["commands_dir"]}','Bot','system')

    for command_name, module_file in config["commands"].items():
        module_path = os.path.join(config["system"]["commands_dir"], module_file)
        if not os.path.exists(module_path):
            log(f"Файл команды {command_name} не найден: {module_path}", "Bot", color='error')
            continue

        spec = importlib.util.spec_from_file_location(f"commands.{command_name}", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, "handle_command"):
            command_handlers[command_name] = module.handle_command
            log(f"Команда {command_name} загружена", 'Bot', color='done')
        else:
            log(f"Команда {command_name} не имеет функцию handle_command", "Bot", 'strong')
    log(f'Загружено команд: {len(command_handlers)}', 'Database')

    # Загружаем пользователей
    log('Загрузка пользователей:', 'Database', 'system')
    for user_data in Data.getUser():
        try:
            user = UserClass(user_data["userid"], user_data['username'], bot, Data,command_handlers)
            UserClass.List.add(user)
            log(f'Пользователь {user.getUsername()}:{user.getUserid()} загружен', 'Database', 'done')
        except Exception as error:
            log(f'Ошибка {error} при загрузки пользователя {user.getUsername()}:{user.getUserid()}', 'Database',
                'error')
    log(f'Загружено пользователей: {len(UserClass.List.Users)}', 'Database')

    # Регистрация обработчика команд
    @bot.message_handler()
    def messageRoute(message):
        if config["system"]["prefix"] in message.text:
            command = message.text.split()[0].replace(config["system"]["prefix"], "")
            if command=='start' and UserClass.List.find(message.chat.id)==None:
                try:
                    newuser=UserClass(message.chat.id,message.from_user.username,bot,Data,command_handlers)
                    newuser.__register__()
                    UserClass.List.add(newuser)
                    log(f'Пользователь {newuser.getUsername()}:{newuser.getUserid()} добавлен','Database','done')
                except Exception as error:
                    log(f'Ошибка {error} при добавлении пользователь {message.from_user.username}:{message.chat.id}', 'Database', 'error')
            command_handler(command,message)

    @bot.callback_query_handler(func=lambda callback: True)
    def callbackRoute(callback):
        command_handler(callback.data,callback.message)


    def command_handler(command,message):
        args = message.text.split()
        del args[0]
        if command in command_handlers:
            execUser=UserClass.List.find((message.chat.id))
            print(f">>>{message.text}")
            command_handlers[command](message,execUser,args)
        else:
            bot.reply_to(message, 'Такой команды не существует :(')



def shutdown():
    log('Бот выключен','Bot','system')
    bot.stop_polling()
    sys.exit(0)

# Только при прямом запуске выполняем инициализацию
if __name__ == "__main__":
    log('Бот включен', 'Bot', 'system')
    initialize_bot()
    bot.polling(non_stop=True,skip_pending=True)
    # Thread(target=timer()).start()

atexit.register(shutdown())





