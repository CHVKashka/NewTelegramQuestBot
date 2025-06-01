from telebot import types
import json
with open("settings.json", encoding='utf-8') as config_file:
    config = json.load(config_file)

def handle_command(message,user,args):
    markup=types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Помощь', callback_data='callback_help'))
    markup.add(types.InlineKeyboardButton('Создать комнату', callback_data='callback_create_lobby'))
    markup.add(types.InlineKeyboardButton('Присоединиться к комнате', callback_data='callback_join_lobby'))
    print(user.sendMessage(config['text']['start'],markups=markup))