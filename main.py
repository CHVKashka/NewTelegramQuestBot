import atexit
import importlib.util
import json
import os
import sys
import telebot
from colorama import init
from database import SQLiteDatabase
from utils import *
import time as t




# Инициализация
with open("settings.json", encoding='utf-8') as config_file:
    config = json.load(config_file)

bot = telebot.TeleBot(config["system"]["token"])
init()
data = SQLiteDatabase(db_path='data.SQLITE3')

# Загрузка команд
command_list = {}
log(f'Загрузка файлов команд из {config["system"]["commands_dir"]}', 'Bot', 'system')

for command_name, module_file in config["commands"].items():
    module_path = os.path.join(config["system"]["commands_dir"], module_file)
    if not os.path.exists(module_path):
        log(f"Файл команды {command_name} не найден: {module_path}", "Bot", color='error')
        continue

    spec = importlib.util.spec_from_file_location(f"commands.{command_name}", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if hasattr(module, "handle_command"):
        command_list[command_name] = module.handle_command
        log(f"Команда {command_name} загружена", 'Bot', color='done')
    else:
        log(f"Команда {command_name} не имеет функцию handle_command", "Bot", 'strong')
log(f'Загружено команд: {len(command_list)}', 'Database')
#return bot, data, command_list, config


@bot.message_handler()
def messageRoute(message):
    if config["system"]["prefix"] in message.text:
        message_strip = message.text.split(' ')
        command = message_strip[0].replace(config["system"]["prefix"], "")
        del message_strip[0]
        if command == 'start' and data.getUser(message.chat.id) == []:
            data.addUser(message.chat.id, message.from_user.username, message.message_id)

        command_handler(command, message, args={},strip_command=message_strip)


@bot.callback_query_handler(func=lambda callback: True)
def callbackRoute(callback):
    callback_strip = callback.data.split('#')
    command = callback_strip[0]


    command_handler(command, callback.message, args={},strip_command=callback_strip)


def command_handler(command, message, args, strip_command=None):
    #print(command,strip_command)
    if strip_command is not None:
        for arg in strip_command:
            if ":" in arg:
                striped_arg = arg.split(':')
                args.update({striped_arg[0]: striped_arg[1]})
            else:
                try:
                    keys = list(args.keys())
                    maxId = []
                    for elem in keys:
                        maxId.append(int(elem.replace('arg', '')))
                    maxId = max(maxId)
                except ValueError:
                    maxId = 0
                args.update({f'arg{maxId + 1}': arg})
    if command in command_list:
        retry=None
        try:
            retry = command_list[command](message, bot, data, command_list, args)
            log(f'Пользователь {message.chat.id} вызвал команду {command}:{args}','Bot')
        except Exception as error:
            log(f'Ошибка {error} при вызове команды {command} пользователем {message.chat.id}','Bot','error')
            raise error
            
        if retry is not None:
            command_handler(retry.get('callback'),retry.get('message'),retry.get('args'))
    else:
        bot.reply_to(message, 'Такой команды не существует :(')


def shutdown():
    log('Бот выключен', 'Bot', 'system')
    bot.stop_polling()
    sys.exit(0)


# Только при прямом запуске выполняем инициализацию
if __name__ == "__main__":
    t.sleep(1)
    log('Бот включен', 'Bot', 'system')
    bot.polling(non_stop=True, skip_pending=True)
    # Thread(target=timer()).start()

atexit.register(shutdown())
