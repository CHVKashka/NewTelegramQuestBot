from telebot import types
def handle_command(message,user,args):
    markup=types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('ping',callback_data='ping'))
    user.sendMessage('pong',markups=markup)
    #bot.send_message(message.chat.id, 'pong',reply_to_message_id=message.message_id,reply_markup=murkup)
