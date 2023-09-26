from channels.generic.websocket import WebsocketConsumer
from random import randint
from time import sleep
import json

class WSConsumer(WebsocketConsumer):
    # def connect(self):
        # self.accept()
        
        # self.send(json.dumps({'message': 'Hello World!', 'id': randint(1, 100)}))
    def connect(self):
        self.accept()
        self.group_name = "train_progress_group"  # Đặt tên nhóm WebSocket

    def disconnect(self, close_code):
        pass

    def send_progress(self, event):
        progress = event["progress"]
        self.send(json.dumps({"progress": progress}))

    def receive(self, text_data):
        pass

    def send_message(self, message):
        self.send(json.dumps({"message": message}))
        