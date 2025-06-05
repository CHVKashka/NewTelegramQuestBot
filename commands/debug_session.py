from utils import log
def handle_command(message, bot, data, command_list, args):
    match args.get('arg1'):
        case 'delete':
            try:
                data.removeSession(int(args.get('arg2')))
                bot.send_message(message.chat.id, f'Сессия {args.get("arg2")} удалена')
            except Exception as error:
                bot.send_message(message.chat.id, f'Ошибка удаления сессии')
                log(f'Ошибка удаления сессии {args.get("arg1")}: {error}','Session','error')

        case 'add':
            try:
                #Переписать под новый стандарт вызова функций
                command_list['callback_create_session'](args.get("arg0"), args.get("arg1"), args.get("arg2"),args.get("arg3"))
            except Exception as error:
                bot.send_message(message.chat.id, f'Ошибка создания сессии')
                log(f'Ошибка создания сессии: {error}', 'Session', 'error')

