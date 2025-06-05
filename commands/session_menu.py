import json
from telebot import types
from utils import log


with open("settings.json", encoding='utf-8') as config_file:
    config = json.load(config_file)


def handle_command(message, bot, data, command_list, args):
    session = data.getSessionData(args['s_id'])
    user = next((u for u in session if u['user_id'] == message.chat.id), None)
    user_data=data.getUser(user.get('user_id'))[0]
    match args['act']:
        case 'create':
            # print(data.getUser(session[0]['user_id'])[0]['menu_id'])
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('Обратно к интерфейсу',
                                                  callback_data=f'session_menu#act:open#s_id:{args['s_id']}'))
            bot.edit_message_text(chat_id=message.chat.id, message_id=user_data.get('menu_id'),
                                  text=config['text']['session_menu_redact'], reply_markup=markup)
            data.updateUser(message.chat.id, {'opened_menu': 'session'})

        case 'open':
            markup = types.InlineKeyboardMarkup()
            if user.get('is_admin') > 0:
                markup.add((types.InlineKeyboardButton('Открыть панель администратора',
                                                       callback_data=f'session_menu#act:admin#s_id:{args['s_id']}')))
            markup.add((types.InlineKeyboardButton('Вернуться в меню', callback_data='start')))
            # использованы короткие аргументы, т.к. Телеграм отказывается передовать много больших
            markup.add(types.InlineKeyboardButton(f'Покинуть сессию',
                                                  callback_data=f'callback_exit_session#s_id:{args["s_id"]}#user_id:{user.get("user_id")}'))
            try:
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=user_data.get('menu_id'),
                                      text=config['text']['session_menu_view'], reply_markup=markup)
            except Exception as error:
                msg = bot.send_message(message.chat.id, config['text']['session_menu_view']).message_id
                data.updateUser(message.chat.id, {'menu_id': msg})
                raise error

            data.updateUser(message.chat.id, {'opened_menu': 'session'})

        case 'admin':
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('Обратно к интерфейсу',
                                                  callback_data=f'session_menu#act:open#s_id:{args['s_id']}'))
            markup.add(types.InlineKeyboardButton('Удалить комнату',
                                                  callback_data=f'callback_delete_session#s_id:{args["s_id"]}#user_id:{user.get("user_id")}'))
            try:
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=user_data.get('menu_id'),
                                      text=config['text']['session_menu_view'], reply_markup=markup)
            except Exception as error:
                print(error)
                msg = bot.send_message(message.chat.id, config['text']['session_menu_view']).message_id
                data.updateUser(message.chat.id, {'menu_id': msg})

            data.updateUser(message.chat.id, {'opened_menu': 'session'})

        case 'del':
            markup = types.InlineKeyboardMarkup()
            markup.add((types.InlineKeyboardButton('Вернуться в меню', callback_data='start')))
            try:
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=user_data.get('menu_id'),
                                      text='Комната была удалена', reply_markup=markup)
            except Exception as error:
                print(error)
                msg = bot.send_message(message.chat.id, 'Комната была удалена').message_id
                data.updateUser(message.chat.id, {'menu_id': msg})

