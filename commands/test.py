def handle_command(message, bot, data,command_list, args):
    bot.send_message(message.chat.id, 'Введите сообщение:')
    bot.register_next_step_handler(message,command_list.get('test2'),bot,data,command_list,args)