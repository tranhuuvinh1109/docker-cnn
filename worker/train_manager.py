# train_manager.py

import threading
import queue
from interger.consumers import *

class TrainManagerThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.queue = queue.Queue()

    def run(self):
        while True:
            model_params = self.queue.get()
            if model_params is None:
                break
            model_name = model_params['model_name']

            # Gọi hàm train_func() để huấn luyện mô hình
            train_func(model_name)

            # Cache kết quả của mô hình vào một hệ thống cache

train_manager_thread = TrainManagerThread()
train_manager_thread.start()
