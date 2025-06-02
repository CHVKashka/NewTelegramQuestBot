from telebot import types
def handle_command(message, bot, data,command_list, args):
    markup=types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('ping',callback_data='ping'))
    bot.send_message(message.chat.id,'ping',reply_markup=markup)