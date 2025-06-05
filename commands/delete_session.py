def handle_command(message, bot, data, command_list, args):
    bot.send_message(message.chat.id, 'Вы действительно хотите удалить комнату?\nВведите "удалить" для подтверждения')
    bot.register_next_step_handler(message, deleteSession, bot, data, command_list, args)


def deleteSession(message, bot, data, command_list, args):
    if message.text.lower() == 'удалить':
        data.updateUser(message.chat.id, {'session_id': 0})
        command_list['start'](message, bot, data, command_list, args)
        session=data.getSessionData(args.get("s_id"))
        args.update({'act':'del'})
        print(session)
        print(args)
        for user in session:
            if user.get('is_admin')!=2:
                print(message.chat.id)
                data.updateUser(user.get('user_id'),{'session_id':0})
                message.chat.id = user.get('user_id')
                command_list['session_menu'](message, bot, data, command_list, args)
        data.removeSession(args.get('s_id'))
    else:
        return None
