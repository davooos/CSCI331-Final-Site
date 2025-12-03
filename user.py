import uuid
from chat import Chat
from chat import Message
from datetime import datetime

class User:
    def __init__(self, session, session_id):
        self.session = session
        self.session_id = session_id
        self.chatbot = Chat()
        self.last_active = datetime.now()
        self.messages = [Message("Tubby", "Hello! What is your name?")]

    def get_session_id(self):
        return self.session_id

    def get_chatbot(self):
        return self.chatbot

    def update_last_active(self):
        self.last_active = datetime.now()

    def set_session_id(self):
        self.session['session_id'] = self.session_id

    def cleanup(self):
        del self.chatbot
        self.session.clear()