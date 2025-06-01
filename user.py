from psutil import users
from utils import log

class UserClass():
    def __init__(self,userid,username,bot,database_instance,handler_instance):
        self.userid=userid
        self.username=username
        self.database_instance=database_instance
        self.bot_instance=bot
        self.handler_instance=handler_instance

    def __register__(self):
        self.database_instance.addUser(self.userid, self.username)

    def getUserid(self):
        return self.userid

    def getUsername(self):
        return self.username

    def getBotInstance(self):
        return self.bot_instance

    def sendMessage(self,text,markups=None):
        return (self.bot_instance.send_message(self.userid, text, reply_markup=markups, parse_mode='html')).message_id

    def editMessage(self):
        pass

    def awaitUserMessage(self,message,call_func,user,args):
        self.bot_instance.register_next_step_handler(message, self.handler_instance[f"{call_func}"],user,args)

    def addMessage(self):
        self.database_instance.addMessage(self.userid, self.lastMessage.message_id)

    def deleteMessages(self):
        try:
            messagesid=self.database_instance.getMessage(self.userid)
        except Exception as error:
            log(f'Ошибка {error} при получении сообщений пользователя {self.username},{self.userid}','UserClass',"error")
            return
        for messageid in messagesid:
            try:
                self.database_instance.removeMessages(self.userid)
                self.bot_instance.delete_message(self.userid, messagesid)
                log(f'Удалено сообщение {messageid}, пользователь {self.username},{self.userid}',"UserClass")
            except Exception as error:
                log(f'Ошибка {error} при удалении сообщения {messageid}, пользователь {self.username},{self.userid}')
                return



    class List:
        Users={}
        @classmethod
        def add(cls, user):
            cls.Users[f"{user.getUserid()}"] = user

        @classmethod
        def remove(cls, user):
            cls.Users.update({user.getUserid(): user})
            cls.datab

        @classmethod
        def overwrite(cls, array):
            cls.Users = array

        @classmethod
        def find(cls, userid):
            return cls.Users.get(str(userid))











