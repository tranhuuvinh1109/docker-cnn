from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
import json
from rest_framework.authtoken.models import Token
from .serializers import *
from .emails import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import ssl
from django.shortcuts import get_object_or_404
from export import views as export_views
from tensorflow.keras.applications.resnet50 import preprocess_input
from io import BytesIO
import os
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import tensorflow as tf
import numpy as np
from PIL import Image
from .models import User 

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from django.contrib.auth import authenticate



from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

# Vô hiệu hóa kiểm tra chứng chỉ SSL
ssl._create_default_https_context = ssl._create_unverified_context
class UserSerializerNested(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.EmailField()
    avatar = serializers.CharField()
    username = serializers.CharField()

class ProjectSerializer(serializers.ModelSerializer):
    user = UserSerializerNested()

    class Meta:
        model = Project
        fields = ['id', 'user', 'progress', 'status', 'link_drive']


class RegisterAPI(APIView):
    def post(self, request):
        data = request.data
        serializers = UserSerializer(data=data)
        if serializers.is_valid():
            serializers.save()
            send_otp_via_email(serializers.data['email'])
            return Response({
                'status': 200,
                'message': 'User registered successfully, please check your Email to confirm',
                'data': serializers.data
            })

        return Response({
            'status': 400,
            'message': 'User registration failed, please try again',
            'data': serializers.errors
        })


class VerifyOTP(APIView):
    def post(self, request):
        try:
            data = request.data
            serializers = VerifyAccountSerializer(data=data)
            if serializers.is_valid():
                email = serializers.data['email']
                otp = serializers.data['otp']
                user = User.objects.filter(email=email)
                if not user.exists():
                    return Response({
                        'status': 400,
                        'message': 'User registration failed, please try again',
                        'data': 'invalid email'
                    })

                if not user[0].otp == otp:
                    return Response({
                        'status': 400,
                        'message': 'User registration failed, please try again',
                        'data': 'wrong OTP'
                    })

                user = user.first()
                user.is_verified = True
                user.save()

                return Response({
                    'status': 200,
                    'message': 'Account has been verified',
                    'data': {
                        'email': user.email
                    }
                })

            else:
                return Response({
                    'status': 400,
                    'message': 'User registration failed, please try again',
                    'data': serializers.errors
                })

        except Exception as e:
            return JsonResponse(json.dumps(e))


class LoginAPI(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        # Kiểm tra xem email và password đã được cung cấp
        if not email or not password:
            return Response({
                'status': 400,
                'message': 'Email and password are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Xác thực người dùng
        user = authenticate(request, username=email, password=password)

        if user is not None:
            # Tạo hoặc lấy token cho người dùng
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'status': 200,
                'message': 'User login successful',
                'data': {
                    'token': token.key,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                    }
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 400,
                'message': 'Wrong email or password, please try again.',
            }, status=status.HTTP_400_BAD_REQUEST)


class CreateProjectAPI(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        progress = request.data.get('progress')
        status_text = request.data.get('status')
        link_drive = request.data.get('link_drive')
        file = request.FILES.get("file")

        try:
            user = User.objects.get(id=user_id)
            print(">>>user -->:", user)
        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        project = Project.objects.create(
            user=user, progress=progress, status=status_text, link_drive=link_drive)
        print("Project created -->0", project)
        # unzip file
        export_views.UploadAndUnzip.unzipFile(file, 'project_4')
        # Serialize dự án
        serializer = ProjectSerializer(project)

        response_data = {
            'message': 'Project created successfully',
            'data': serializer.data
        }
        print("--> before serializing project")

        return Response(response_data, status=status.HTTP_201_CREATED)


class InforUser(APIView):
    def get(self, request, user_id):
        try:
            # Lấy thông tin người dùng với user_id
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        projects = Project.objects.filter(user=user)
        serializer = ProjectSerializer(projects, many=True)
        user_data = UserSerializerNested(user).data
        response_data = {
            'message': f'Information for user with id {user_id}',
            'data': {
                'user': user_data,
                'projects': serializer.data
            }
        }
        return Response(response_data, status=status.HTTP_200_OK)

class Me(APIView):
    def post(self, request):
        data = request.data
        token_key = data.get('token')
        if not token_key:
            return Response({"error": "Token not provided"}, status=status.HTTP_404_NOT_FOUND)
        try:
            token = Token.objects.get(key=token_key)
        except Token.DoesNotExist:
            return Response({"error": "Invalid token"}, status=status.HTTP_404_NOT_FOUND)

        user = token.user
        serializer = UserSerializer(user)
        return Response({"message": "Token processed successfully", "data": { 'token': token_key, 'user': serializer.data}})

class UpdateProjectStatus(APIView):
    def post(self, request, project_id):
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({"message": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
        new_status = request.data.get('status', None)
        if new_status is None:
            return Response({"message": "Status is required"}, status=status.HTTP_400_BAD_REQUEST)

        project.status = new_status
        project.save()

        serializer = ProjectSerializer(project)
        response_data = {
            'message': 'Project status updated successfully',
            'data': serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)


class UpdateProject(APIView):
    def put(self, request):
        project_data = request.data
        try:
            project_id = project_data.get('id')
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({"message": "Project not found"}, status=status.HTTP_404_NOT_FOUND)

        project.status = project_data.get('status', project.status)
        project.link_drive = project_data.get('linkDrive', project.link_drive)
        project.save()

        serializer = ProjectSerializer(project)
        response_data = {
            'message': 'Project updated successfully',
            'data': serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)


class UserDataManageAPI(APIView):
    def get(self, request):
        users = User.objects.all()
        data_list = []

        for user in users:
            user_serializer = UserSerializer(user)

            projects = Project.objects.filter(user=user)
            project_serializer = ProjectSerializer(projects, many=True)
            user_data = {
                "user": user_serializer.data,
                "projects": project_serializer.data
            }
            data_list.append(user_data)
        response_data = {
            "message": "Get data user manage project successful",
            "data": data_list
        }

        return Response(response_data, status=status.HTTP_200_OK)


model_path = 'D:/Django/CNN/docker-cnn/model/bike_car.h5'
model = tf.keras.models.load_model(model_path)


class DetectImage(APIView):
    def post(self, request):
        # Kiểm tra xem có file hình ảnh được gửi lên không
        if 'image' not in request.FILES:
            return Response({'message': 'No image uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        # Đọc file ảnh từ request.FILES
        image_file = request.FILES['image']

        # Đọc ảnh từ buffer
        img = Image.open(image_file)
        img = img.convert('RGB')  # Chuyển đổi thành ảnh màu nếu không phải

        # Thực hiện nhận diện trên ảnh
        predicted_label, confidence = self.detect_label(img)

        # Chuyển đổi độ tin cậy thành phần trăm
        confidence_percentage = confidence * 100

        # Chuẩn bị phản hồi
        response_data = {
            'message': 'Detection successful',
            'predicted_label': predicted_label,
            # Hiển thị độ tin cậy dưới dạng phần trăm
            'confidence': f'{confidence_percentage:.2f}%'

        }

        return Response(response_data, status=status.HTTP_200_OK)

    def detect_label(self, img):
        # Tiền xử lý ảnh
        # Thay đổi kích thước ảnh theo model của bạn
        img = img.resize((128, 128))
        img = np.array(img)
        img = np.expand_dims(img, axis=0)
        img = preprocess_input(img)

        # Dự đoán
        predictions = model.predict(img)
        predicted_class_index = np.argmax(predictions[0])
        class_labels = ['Bike', 'Car']  # Thay bằng danh sách nhãn của bạn
        predicted_class = class_labels[predicted_class_index]

        # Lấy confidence (độ tin cậy)
        confidence = predictions[0][predicted_class_index]

        return predicted_class, confidence
