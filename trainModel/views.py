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

train_data_dir = 'D:/Django/CNN/docker-cnn/datasets/train'
test_data_dir = 'D:/Django/CNN/docker-cnn/datasets/valid'

img_width, img_height = 128, 128
batch_size = 32

class TrainModel (APIView):
    def get(self, request):
        # Tạo data generator cho việc augmentation dữ liệu (tuỳ chọn)
        train_datagen = ImageDataGenerator(
            rescale=1.0 / 255.0,  # Rescale giá trị pixel về khoảng [0, 1]
            rotation_range=20,    # Xoay ảnh ngẫu nhiên
            width_shift_range=0.2,  # Dịch ảnh ngang ngẫu nhiên
            height_shift_range=0.2, # Dịch ảnh dọc ngẫu nhiên
            shear_range=0.2,       # Biến dạng ảnh
            zoom_range=0.2,        # Phóng to/Thu nhỏ ngẫu nhiên
            horizontal_flip=True,  # Lật ảnh ngang ngẫu nhiên
            fill_mode='nearest'    # Điền giá trị pixel bị thiếu bằng giá trị gần nhất
        )
        
        # Load và tiền xử lý dữ liệu huấn luyện dựa trên tên thư mục con
        train_generator = train_datagen.flow_from_directory(
            train_data_dir,
            target_size=(img_width, img_height),
            batch_size=batch_size,
            class_mode='categorical'  # Sử dụng 'categorical' cho bài toán phân loại nhiều lớp
        )
        # Tạo một mô hình CNN đơn giản
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
        # Biên dịch mô hình
        model.compile(optimizer='adam',
                    loss='categorical_crossentropy',
                    metrics=['accuracy'])

        # Huấn luyện mô hình với callback tính thời gian
        epochs = 10
        model.fit(
            train_generator,
            epochs=epochs,
        )
        # Lưu mô hình đã huấn luyện
        model.save('D:/Django/CNN/docker-cnn/model/trained_new1.h5')
        
        # Load mô hình đã huấn luyện
        model = load_model('D:/Django/CNN/docker-cnn/model/trained_new1.h5')
        
        # Đường dẫn tới ảnh cần dự đoán
        image_path = 'D:/Django/CNN/docker-cnn/datasets/Bike.jpeg'

        # Đọc và tiền xử lý ảnh
        img = image.load_img(image_path, target_size=(img_width, img_height))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array /= 255.0
        # Dự đoán
        predictions = model.predict(img_array)
        # Lấy chỉ mục của lớp dự đoán và nhãn
        predicted_class_index = np.argmax(predictions[0])
        class_labels = list(train_generator.class_indices.keys())
        predicted_class = class_labels[predicted_class_index]
        # Lấy điểm tự tin của dự đoán
        confidence_score = predictions[0][predicted_class_index] * 100

        # In ra lớp dự đoán và điểm tự tin
        print(f"Predicted class for the image is: {predicted_class}")
        print(f"Confidence: {confidence_score:.2f}%")
        
        return Response({"predicted_class": predicted_class, "confidence_score": confidence_score}, status=status.HTTP_200_OK)

