def handle_command(message, bot, data, command_list, args):
    get_next_id = lambda arr: max((x['session_id'] for x in arr), default=0) + 1
    data.createSession(get_next_id(data.getSessionList()), message.chat.id, message.from_user.username)
    bot.send_message(message.chat.id, 'Сессия создана')
