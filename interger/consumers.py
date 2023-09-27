from time import sleep
from channels.generic.websocket import WebsocketConsumer
from random import randint
import json
from upload.views import *
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
# from tensorflow.keras.preprocessing import image
progress = 0
train_data_dir = 'D:/Django/CNN/docker-cnn/datasets/train'
test_data_dir = 'D:/Django/CNN/docker-cnn/datasets/valid'

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
        epochs = 3
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