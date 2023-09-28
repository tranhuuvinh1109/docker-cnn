from time import sleep
from channels.generic.websocket import WebsocketConsumer
from random import randint
import json
from upload.views import *
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
# from tensorflow.keras.preprocessing import image


import os

# Đường dẫn đến thư mục gốc chứa dữ liệu
base_data_dir = 'D:/Django/CNN/docker-cnn/datasets'

# Liệt kê tất cả các thư mục con trong thư mục "datasets"
data_folders = [folder for folder in os.listdir(base_data_dir) if os.path.isdir(os.path.join(base_data_dir, folder))]

# Chọn một thư mục con (ví dụ: chọn thư mục đầu tiên)
if data_folders:
    data_folder_name = data_folders[0]
else:
    data_folder_name = 'default_folder'  # Thư mục mặc định nếu không có thư mục con

# Tạo đường dẫn linh hoạt
train_data_dir = os.path.join(base_data_dir, data_folder_name, 'train')
test_data_dir = os.path.join(base_data_dir, data_folder_name, 'valid')

# print('folder is: ', data_folders)

progress = 0


img_width, img_height = 128, 128
batch_size = 32
class WSConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        train_datagen = ImageDataGenerator(
            rescale=1.0 / 255.0,  # Rescale giá trị pixel về khoảng [0, 1]
            rotation_range=20,    # Xoay ảnh ngẫu nhiên
            width_shift_range=0.2,  # Dịch ảnh ngang ngẫu nhiên
            height_shift_range=0.2, # Dịch ảnh dọc ngẫu nhiên
            shear_range=0.2,       # Biến dạng ảnh
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
        print(f"---->>>>>>>Start")
        self.send(json.dumps({'message': 'Hello World!', 'id': 'START'}))
        
        for epoch in range(epochs):
            progress = ++epoch
            print(f"---->>>>>>>Epoch {epoch + 1}/{epochs}")
            model.fit(
                train_generator,
                epochs=1, 
            )
            self.send(json.dumps({'message': 'Hello World!', 'id': progress}))
            
            
        model.save('D:/Django/CNN/docker-cnn/model/trained_new1.h5')
        upload_folder('D:/Django/CNN/docker-cnn/model/trained_new1.h5', 'model_trained')
        self.send(json.dumps({'message': 'Hello World!', 'id': 'DONE'}))
        print("savingg =>>>>")
        
        # os.remove(data_folders)
        # print("removing datasets folders")