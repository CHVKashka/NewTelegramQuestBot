def handle_command(message, bot, data, command_list, args):
    bot.send_message(message.chat.id,'Введите invite код комнаты:')
    bot.register_next_step_handler(message, joinSession,bot, data, command_list, args)


def joinSession(message, bot, data, command_list, args):
    session_code=message.text.lower()
    session=next((u for u in data.getSessionList() if u['session_code'] == session_code), None)
    user=data.getUser(message.chat.id)[0]
    if session:
        if user.get('session_id')==0:
            bot.send_message(message.chat.id,'Вы присоединились к сессии')
            data.joinSession(session.get('session_id'),message.chat.id,message.chat.username)
            data.updateUser(message.chat.id,{'session_id':session.get('session_id')})
            print(message.chat.id,{'session_id':session.get('session_id')})
            command_list['session_menu'](message, bot, data, command_list, args={'s_id':session.get('session_id'),'act':'open'})
        else:
            bot.send_message(message.chat.id, 'Вы уже находитесь в сессии')
    else:
        bot.send_message(message.chat.id, 'Сесси не существует или введён неправильный код')
    

    print(session)
