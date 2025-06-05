def handle_command(message, bot, data,command_list, args):
    bot.send_message(message.chat.id, f'Введите сообщение {args}:')
    bot.register_next_step_handler(message,command_list.get('test2'),bot,data,command_list,args)