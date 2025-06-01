from telebot import types
import json

with open("settings.json", encoding='utf-8') as config_file:
    config = json.load(config_file)

def handle_command(message,user,args):
    user.sendMessage(config['text']['help'])