from time import sleep
from channels.generic.websocket import WebsocketConsumer
import json
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
import os
import threading
import multiprocessing
from queue import Queue
import random
from upload.views import upload_folder

# Đường dẫn đến thư mục gốc chứa dữ liệu
base_data_dir = 'D:/Django/CNN/docker-cnn/datasets'

# Danh sách các thư mục cần đào tạo
data_folders = ['bikeCar', 'catDog']

img_width, img_height = 128, 128
batch_size = 32

# Hàng đợi để quản lý việc đào tạo các thư mục
training_queue = Queue()

class WSConsumer(WebsocketConsumer):
    def train(self, train_data_dir):
        train_datagen = ImageDataGenerator(
            rescale=1.0 / 255.0,
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True,
            fill_mode='nearest'
        )
        train_generator = train_datagen.flow_from_directory(
            train_data_dir,
            target_size=(img_width, img_height),
            batch_size=batch_size,
            class_mode='categorical'
        )
        model = Sequential([
            Conv2D(32, (3, 3), activation='relu', input_shape=(img_width, img_height, 3)),
            MaxPooling2D((2, 2)),
            Conv2D(64, (3, 3), activation='relu'),
            MaxPooling2D((2, 2)),
            Conv2D(128, (3, 3), activation='relu'),
            MaxPooling2D((2, 2)),
            Flatten(),
            Dense(128, activation='relu'),
            Dense(len(train_generator.class_indices), activation='softmax')
        ])
        model.compile(optimizer='adam',
                    loss='categorical_crossentropy',
                    metrics=['accuracy'])
        epochs = 5
        self.send(json.dumps({'message': f'Training started for folder {train_data_dir}', 'training': {
                'name': train_data_dir,
                'progress': 0,
                'linkDrive': '',
                'status': 'training'
            }}))
        
        for epoch in range(epochs):
            progress = (epoch + 1) / epochs * 100
            dataProject = {
                'name': train_data_dir,
                'progress': progress,
                'linkDrive': '',
                'status': 'training'
            }
            self.send(json.dumps({'message': 'Hello World!', 'id': progress, 'training': dataProject}))
            model.fit(train_generator, epochs=1)
            
        num = random.random()
        file_name = f'D:/Django/CNN/docker-cnn/model/{num:.6f}.h5'
        model.save(file_name)
        link = upload_folder(file_name, 'model_trained')
        dataProject2 = {
                'name': train_data_dir,
                'progress': progress,
                'linkDrive': link,
                'status': 'done'
            }
        self.send(json.dumps({'message': 'Hello World!', 'link': link, 'training':dataProject2}))
        print(f"Saving model for folder {train_data_dir} => {link}")
    
    def train_wrapper(self):
        while not training_queue.empty():
            train_data_dir = training_queue.get()
            self.train(train_data_dir)
            training_queue.task_done()
    
    def connect(self):
        self.accept()
        data = [
            {
                'id': 1,
                'name': 'D:/Django/CNN/docker-cnn/datasets\\bikeCar\\train',
                'progress': 0,
                'linkDrive': '',
                'status': 'none'
            },
            {
                'id': 2,
                'name': 'D:/Django/CNN/docker-cnn/datasets\\catDog\\train',
                'progress': 0,
                'linkDrive': '',
                'status': 'none'
            }
        ]
        self.send(json.dumps({'message': 'Hello Connected!', 'projects': data}))
        threads = []

        # Thêm các thư mục vào hàng đợi để đào tạo
        for folder_name in data_folders:
            train_data_dir = os.path.join(base_data_dir, folder_name, 'train')
            training_queue.put(train_data_dir)
        
        # Khởi tạo và chạy worker (tiến trình con) với các thread
        num_workers = 1  # Số lượng worker bạn muốn sử dụng
        for _ in range(num_workers):
            worker = threading.Thread(target=self.train_wrapper)
            worker.start()
            threads.append(worker)
        
        # Chờ tất cả các worker hoàn thành
        for worker in threads:
            worker.join()
        
        self.send(json.dumps({'message': 'All training completed.'}))

    def disconnect(self, close_code):
        self.close()
