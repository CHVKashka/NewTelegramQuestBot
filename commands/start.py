from telebot import types
import json

with open("settings.json", encoding='utf-8') as config_file:
    config = json.load(config_file)


def handle_command(message, bot, data, command_list, args):
    user = data.getUser(message.chat.id)[0]
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Помощь', callback_data='callback_help'))
    print(user.get('session_id'))
    if user.get("session_id") == 0:
        markup.add(types.InlineKeyboardButton('Создать комнату', callback_data='callback_create_session'))
        markup.add(types.InlineKeyboardButton('Присоединиться к комнате', callback_data='callback_join_session'))
    else:
        markup.add(types.InlineKeyboardButton('Вернуться к комнате',
                                              callback_data=f'session_menu#act:open#s_id:{user.get('session_id')}'))
    try:
        bot.delete_message(chat_id=message.chat.id,message_id=user.get('menu_id'))
    except Exception as error:
        print(error)

    msg = (bot.send_message(message.chat.id, config['text']['start'], reply_markup=markup)).message_id
    data.updateUser(message.chat.id, {"menu_id": msg,'opened_menu': 'start'})
