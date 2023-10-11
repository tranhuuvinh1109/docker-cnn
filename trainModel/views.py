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

training_queue = Queue()

img_width, img_height = 128, 128
batch_size = 32
training_queue = Queue()

user_id = []
project_id = []
projects_name = []
index_start = 0
class TrainModel:
    def train(self, train_data_dir):
        global user_id, project_id, index_start
        user_id_training = 'user_' + str(user_id[index_start])
        project_id_training = project_id[index_start]
        data_send = {
                'status': 'training',
                'progress': '0',
                'linkDrive': ''
            }
        Firebase.updateProject(user_id_training, project_id_training, data_send)
        
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

        for epoch in range(epochs):
            progress = (epoch + 1) / epochs * 100
            data_send = {
                'status': 'training',
                'progress': progress,
                'linkDrive': ''
            }
            Firebase.updateProject(user_id_training, project_id_training, data_send)
            model.fit(train_generator, epochs=1)

        file_name = f'D:/Django/CNN/docker-cnn/model/{projects_name[index_start]}.h5'
        model.save(file_name)
        # upload to Drive
        data_send = {
                'status': 'push to drive',
                'progress': '100',
                'linkDrive': ''
            }
        Firebase.updateProject(user_id_training, project_id_training, data_send)
        link = upload_folder(file_name, projects_name[index_start])
        # upload to firebase
        data_send = {
                'status': 'done',
                'progress': '100',
                'linkDrive': link
            }
        Firebase.updateProject(user_id_training, project_id_training, data_send)
        index_start += 1

    def train_wrapper(self):
        while not training_queue.empty():
            train_data_dir = training_queue.get()
            self.train(train_data_dir)
            training_queue.task_done()

    def start_training(self):
        threads = []

        # Thêm các thư mục vào hàng đợi để đào tạo
        for folder_name in data_folders:
            parts = folder_name.split('_')[1].split('-')
            train_data_dir = os.path.join(base_data_dir, folder_name, 'train')
            global user_id, project_id,projects_name
            project_id.append(parts[0]) 
            user_id.append(parts[1])
            projects_name.append(folder_name)
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
        trainer.start_training()
        return Response({'message': 'All training completed.'}, status=status.HTTP_200_OK)
