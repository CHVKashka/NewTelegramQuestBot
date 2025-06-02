from telebot import types
import json

with open("settings.json", encoding='utf-8') as config_file:
    config = json.load(config_file)

def handle_command(message, bot, data,command_list, args):
    bot.send_message(message.chat.id,config['text']['help'])