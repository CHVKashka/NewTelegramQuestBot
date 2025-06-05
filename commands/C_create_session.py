from utils import log, char_sequence


def handle_command(message, bot, data, command_list, args):
    nextId=0
    if data.getUser(message.chat.id)[0]['session_id'] == 0:
        try:
            get_next_id = lambda arr: max((x['session_id'] for x in arr), default=0) + 1
            nextId = get_next_id(data.getSessionList())
            data.createSession(nextId, char_sequence(6), message.chat.id,
                               message.chat.username)
            bot.send_message(message.chat.id, 'Сессия создана')
            command_list['session_menu'](message, bot, data, command_list,
                                         args={'session_id': nextId, "act": 'create'})
            log(f"Сессия {nextId} создана пользователем {message.chat.id}", "Session", 'done')
        except Exception as error:
            raise error
            log(f"Ошибка создания сессии пользователем {message.chat.id}: {error}", 'Session', 'error')
    else:
        bot.reply_to(message,
                     'Невозможно создать сессию, так как вы уже находитесь в ней. Пожалуйста выйдите из текущей сессии и попробуйте снова')

    return {'callback': 'session_menu_redact', 'message': message, 'args': {'s_id': nextId, "action": 'create'}}
