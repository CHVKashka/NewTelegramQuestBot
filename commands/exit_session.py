from utils import selector


def handle_command(message, bot, data, command_list, args):
    print(args)
    user = data.FindInSession(args.get('s_id'), args.get('user_id'))

    if user.get('is_admin') == 2:
        bot.send_message(message.chat.id, 'Вы не можете покинуть свою же сессию')
        return None
    else:
        bot.send_message(message.chat.id, 'Вы действительно хотите выйти из сесси? (введите "выход" для подтверждения')

    bot.register_next_step_handler(message, exitSession, bot, data, command_list, user, args)
    return None


def exitSession(message, bot, data, command_list, user, args):
    if message.text.lower() == 'выход':
        data.leaveSession(args.get('s_id'), user.get('user_id'))
        command_list['start'](message, bot, data, command_list, args)
    else:
        return
