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
import shutil
# Đường dẫn đến thư mục gốc chứa dữ liệu
base_data_dir = 'D:/Django/CNN/docker-cnn/datasets'
data_folders = [folder for folder in os.listdir(base_data_dir) if os.path.isdir(os.path.join(base_data_dir, folder))]

img_width, img_height = 128, 128
batch_size = 32

# Hàng đợi để quản lý việc đào tạo các thư mục
training_queue = Queue()


import pyrebase

config = {
    "apiKey": "AIzaSyDXPvGl3y_IWGpU7GvixTL9uEuF0WAyNCk",
    "authDomain": "realtime-cnn.firebaseapp.com",
    "databaseURL": "https://realtime-cnn-default-rtdb.asia-southeast1.firebasedatabase.app",
    "projectId": "realtime-cnn",
    "storageBucket": "realtime-cnn.appspot.com",
    "messagingSenderId": "856972582342",
    "appId": "1:856972582342:web:d4f6747a958fe848b7e6c7"
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
database = firebase.database()


img_width, img_height = 128, 128
batch_size = 32
training_queue = Queue()

def setProject(user_id, project_id, data):
        database.child("data").child(user_id).child(project_id).set(data)
        print('setProject message --->>', data)
        
def updateProject(user_id, project_id, data):
        database.child("data").child(user_id).child(project_id).update(data)
        print('updateProject message --->>', data) 
        
class TrainModel (APIView):
    def train_wrapper():
        while not training_queue.empty():
            train_data_dir = training_queue.get()
            print('train_data_dir: ', train_data_dir)
            training_queue.task_done()
            
    def get(self, request):
        threads = []
        for folder_name in data_folders:
            train_data_dir = os.path.join(base_data_dir, folder_name, 'train')
            training_queue.put(train_data_dir)
        
        data = request.data
        # user_id = data['user_id']
        # project_id = data['project_id']
        user_id = 'user_1'
        project_id = '7'
        
        print("start ===>>")
        data_send = {
            'status': 'chuan bi',
            'progress': '0',
            'linkDrive': ''
        }
        setProject(user_id, project_id, data)
        # Tạo data generator cho việc augmentation dữ liệu (tuỳ chọn)
        train_datagen = ImageDataGenerator(
            rescale=1.0 / 255.0,  # Rescale giá trị pixel về khoảng [0, 1]
            rotation_range=20,    # Xoay ảnh ngẫu nhiên
            width_shift_range=0.2,  # Dịch ảnh ngang ngẫu nhiên
            height_shift_range=0.2,  # Dịch ảnh dọc ngẫu nhiên
            shear_range=0.2,       # Biến dạng ảnh
            zoom_range=0.2,        # Phóng to/Thu nhỏ ngẫu nhiên
            horizontal_flip=True,  # Lật ảnh ngang ngẫu nhiên
            fill_mode='nearest'    # Điền giá trị pixel bị thiếu bằng giá trị gần nhất
        )

        train_generator = train_datagen.flow_from_directory(
            train_data_dir,
            target_size=(img_width, img_height),
            batch_size=batch_size,
            class_mode='categorical'  # Sử dụng 'categorical' cho bài toán phân loại nhiều lớp
        )
        model = Sequential([
            Conv2D(32, (3, 3), activation='relu',
                   input_shape=(img_width, img_height, 3)),
            MaxPooling2D((2, 2)),
            Conv2D(64, (3, 3), activation='relu'),
            MaxPooling2D((2, 2)),
            Conv2D(128, (3, 3), activation='relu'),
            MaxPooling2D((2, 2)),
            Flatten(),
            Dense(128, activation='relu'),
            Dense(len(train_generator.class_indices), activation='softmax')
        ])
        # Biên dịch mô hình
        model.compile(optimizer='adam',
                      loss='categorical_crossentropy',
                      metrics=['accuracy'])

        # Huấn luyện mô hình với callback tính thời gian
        epochs = 5
        for epoch in range(epochs):
            progress = (epoch + 1) / epochs * 100
            print('training progress:________________________', progress)
            data_send = {
                'status': 'training',
                'progress': progress,
                'linkDrive': ''
            }
            updateProject(user_id, project_id, data_send)
            model.fit(train_generator, epochs=1)
        print("before safeeeeeeeeeeeeeeeeeee_____________________________")
        model.save('D:/Django/CNN/docker-cnn/model/trained_new1.h5')
        num_workers = 1
        for _ in range(num_workers):
            worker = threading.Thread(target=self.train_wrapper)
            worker.start()
            threads.append(worker)
        
        for worker in threads:
            worker.join()
        
        print("end fcusldfkjsalkdjflkdsajfldsakjflkdsaglkdsahgkjhdsaglkdsahlfkjds")
        return Response({'message': 'All training completed.'}, status=status.HTTP_200_OK)



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
import shutil
# Đường dẫn đến thư mục gốc chứa dữ liệu
base_data_dir = 'D:/Django/CNN/docker-cnn/datasets'
data_folders = [folder for folder in os.listdir(base_data_dir) if os.path.isdir(os.path.join(base_data_dir, folder))]

img_width, img_height = 128, 128
batch_size = 32

# Hàng đợi để quản lý việc đào tạo các thư mục
training_queue = Queue()

import pyrebase

config = {
    "apiKey": "AIzaSyDXPvGl3y_IWGpU7GvixTL9uEuF0WAyNCk",
    "authDomain": "realtime-cnn.firebaseapp.com",
    "databaseURL": "https://realtime-cnn-default-rtdb.asia-southeast1.firebasedatabase.app",
    "projectId": "realtime-cnn",
    "storageBucket": "realtime-cnn.appspot.com",
    "messagingSenderId": "856972582342",
    "appId": "1:856972582342:web:d4f6747a958fe848b7e6c7"
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
database = firebase.database()


img_width, img_height = 128, 128
batch_size = 32
training_queue = Queue()

def setProject(user_id, project_id, data):
        database.child("data").child(user_id).child(project_id).set(data)
        print('setProject message --->>', data)
        
def updateProject(user_id, project_id, data):
        database.child("data").child(user_id).child(project_id).update(data)
        print('updateProject message --->>', data) 
        
class TrainModel (APIView):
    def train_wrapper():
        while not training_queue.empty():
            train_data_dir = training_queue.get()
            print('train_data_dir: ', train_data_dir)
            training_queue.task_done()
            
    def get(self, request):
        threads = []
        for folder_name in data_folders:
            train_data_dir = os.path.join(base_data_dir, folder_name, 'train')
            training_queue.put(train_data_dir)
        
        data = request.data
        # user_id = data['user_id']
        # project_id = data['project_id']
        user_id = 'user_1'
        project_id = '7'
        
        print("start ===>>")
        data_send = {
            'status': 'chuan bi',
            'progress': '0',
            'linkDrive': ''
        }
        setProject(user_id, project_id, data)
        # Tạo data generator cho việc augmentation dữ liệu (tuỳ chọn)
        train_datagen = ImageDataGenerator(
            rescale=1.0 / 255.0,  # Rescale giá trị pixel về khoảng [0, 1]
            rotation_range=20,    # Xoay ảnh ngẫu nhiên
            width_shift_range=0.2,  # Dịch ảnh ngang ngẫu nhiên
            height_shift_range=0.2,  # Dịch ảnh dọc ngẫu nhiên
            shear_range=0.2,       # Biến dạng ảnh
            zoom_range=0.2,        # Phóng to/Thu nhỏ ngẫu nhiên
            horizontal_flip=True,  # Lật ảnh ngang ngẫu nhiên
            fill_mode='nearest'    # Điền giá trị pixel bị thiếu bằng giá trị gần nhất
        )

        train_generator = train_datagen.flow_from_directory(
            train_data_dir,
            target_size=(img_width, img_height),
            batch_size=batch_size,
            class_mode='categorical'  # Sử dụng 'categorical' cho bài toán phân loại nhiều lớp
        )
        model = Sequential([
            Conv2D(32, (3, 3), activation='relu',
                   input_shape=(img_width, img_height, 3)),
            MaxPooling2D((2, 2)),
            Conv2D(64, (3, 3), activation='relu'),
            MaxPooling2D((2, 2)),
            Conv2D(128, (3, 3), activation='relu'),
            MaxPooling2D((2, 2)),
            Flatten(),
            Dense(128, activation='relu'),
            Dense(len(train_generator.class_indices), activation='softmax')
        ])
        # Biên dịch mô hình
        model.compile(optimizer='adam',
                      loss='categorical_crossentropy',
                      metrics=['accuracy'])

        # Huấn luyện mô hình với callback tính thời gian
        epochs = 5
        for epoch in range(epochs):
            progress = (epoch + 1) / epochs * 100
            print('training progress:________________________', progress)
            data_send = {
                'status': 'training',
                'progress': progress,
                'linkDrive': ''
            }
            updateProject(user_id, project_id, data_send)
            model.fit(train_generator, epochs=1)
        print("before safeeeeeeeeeeeeeeeeeee_____________________________")
        model.save('D:/Django/CNN/docker-cnn/model/trained_new1.h5')
        data_send = {
                'status': 'push drive',
                'progress': '100',
                'linkDrive': 'yyyy'
            }
        updateProject(user_id, project_id, data_send)
        num_workers = 1
        for _ in range(num_workers):
            worker = threading.Thread(target=self.train_wrapper)
            worker.start()
            threads.append(worker)
        
        for worker in threads:
            worker.join()
        
        print("end fcusldfkjsalkdjflkdsajfldsakjflkdsaglkdsahgkjhdsaglkdsahlfkjds")
        return Response({'message': 'All training completed.'}, status=status.HTTP_200_OK)