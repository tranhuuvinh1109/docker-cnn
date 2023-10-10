import pyrebase
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import matplotlib.pyplot as plt
from time import sleep
import os
import threading
import multiprocessing
from queue import Queue
import random
from upload.views import upload_folder
from .uploadToFirebase import Firebase
import shutil


# Đường dẫn đến thư mục gốc chứa dữ liệu
base_data_dir = 'D:/Django/CNN/docker-cnn/datasets'
data_folders = [folder for folder in os.listdir(
    base_data_dir) if os.path.isdir(os.path.join(base_data_dir, folder))]

img_width, img_height = 128, 128
batch_size = 32

# Hàng đợi để quản lý việc đào tạo các thư mục
training_queue = Queue()

# config = {
#     "apiKey": "AIzaSyDXPvGl3y_IWGpU7GvixTL9uEuF0WAyNCk",
#     "authDomain": "realtime-cnn.firebaseapp.com",
#     "databaseURL": "https://realtime-cnn-default-rtdb.asia-southeast1.firebasedatabase.app",
#     "projectId": "realtime-cnn",
#     "storageBucket": "realtime-cnn.appspot.com",
#     "messagingSenderId": "856972582342",
#     "appId": "1:856972582342:web:d4f6747a958fe848b7e6c7"
# }

# firebase = pyrebase.initialize_app(config)
# auth = firebase.auth()
# database = firebase.database()

img_width, img_height = 128, 128
batch_size = 32
training_queue = Queue()

user_id = 'user_1'
project_id = '7'

class TrainModel:
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
        
        print(f"Training model for folder {train_data_dir}...")  # In ra đường dẫn thư mục

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

        for epoch in range(epochs):
            progress = (epoch + 1) / epochs * 100
            data_send = {
                'status': 'training',
                'progress': progress,
                'linkDrive': ''
            }
            Firebase.updateProject(user_id, project_id, data_send)
            model.fit(train_generator, epochs=1)

        num = random.random()
        file_name = f'D:/Django/CNN/docker-cnn/model/{num:.6f}.h5'
        model.save(file_name)
        
        # upload to Drive
        link = upload_folder(file_name, 'model_trained')
        print(f"Saving model for folder {train_data_dir} => {link}")
        
        # upload to firebase
        data_send = {
                'status': 'push drive',
                'progress': '100',
                'linkDrive': link
            }
        Firebase.updateProject(user_id, project_id, data_send)

    def train_wrapper(self):
        while not training_queue.empty():
            train_data_dir = training_queue.get()
            self.train(train_data_dir)
            training_queue.task_done()

    def start_training(self):
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

        print("All training completed.")


trainer = TrainModel()

class TrainModelView(APIView):
    def get(self, request):
        data = request.data
        data_send = {
            'status': 'chuan bi',
            'progress': '0',
            'linkDrive': ''
        }
        Firebase.setProject(user_id, project_id, data)
        
        
        trainer.start_training()
        return Response({'message': 'All training completed.'}, status=status.HTTP_200_OK)
