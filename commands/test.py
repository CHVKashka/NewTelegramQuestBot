def handle_command(message,user,args):
    #bot.send_message(message.chat.id, message,reply_to_message_id=message.message_id)
    user.sendMessage('Введите сообщение:')
    user.awaitUserMessage(message,'test2',user,args)