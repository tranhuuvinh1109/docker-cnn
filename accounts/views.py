from tensorflow.keras.applications.resnet50 import preprocess_input
from io import BytesIO
import os
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import tensorflow as tf
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
import json
import numpy as np
from rest_framework.authtoken.models import Token
from PIL import Image


from .serializers import *
from .emails import *

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import ssl
from .models import *
from django.shortcuts import get_object_or_404


# Vô hiệu hóa kiểm tra chứng chỉ SSL
ssl._create_default_https_context = ssl._create_unverified_context

# Create your views here.


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
        print("->>>>>>>>>>>>>>>>>>>>>>>", request.data)
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
        """
        Login API then response with user data and token
        """
        try:
            serializers = LoginSerializer(data=request.data)

            if serializers.is_valid():
                email = serializers.validated_data['email']
                password = serializers.validated_data['password']

                user = User.objects.filter(email=email)

                if user.exists() and user.count() == 1:
                    user_data = user.first()

                    if user_data.check_password(password):
                        token = Token.objects.get_or_create(user=user_data)
                        return Response({
                            'status': 200,
                            'message': 'User login successful',
                            'data': {
                                'token': token[0].key,
                                'user': UserSerializer(user_data).data
                            }
                        })
                    else:
                        return Response({
                            'status': 400,
                            'message': 'Wrong password or email, please try again',
                        })
                else:
                    return Response({
                        'status': 400,
                        'message': 'User login failed, please try again',
                    })
        except serializers.ValidationError:
            print(serializers.ValidationError)


class CreateProjectAPI(APIView):
    def post(self, request):
        # Lấy dữ liệu đầu vào từ request.data
        user_id = request.data.get('user_id')
        progress = request.data.get('progress')
        status_text = request.data.get('status')
        link_drive = request.data.get('link_drive')

        # Tìm người dùng dựa trên user_id
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Tạo dự án mới với người dùng tìm được
        project = Project.objects.create(
            user=user, progress=progress, status=status_text, link_drive=link_drive)

        # Serialize dự án
        serializer = ProjectSerializer(project)

        response_data = {
            'message': 'Project created successfully',
            'data': serializer.data
        }

        return Response(response_data, status=status.HTTP_201_CREATED)


class InforUser(APIView):
    def get(self, request, user_id):
        try:
            # Lấy thông tin người dùng với user_id
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Lấy danh sách các project của user
        projects = Project.objects.filter(user=user)

        # Serialize danh sách các project
        serializer = ProjectSerializer(projects, many=True)

        # Serialize thông tin người dùng
        user_data = UserSerializerNested(user).data

        # Tạo response chứa thông tin đã được serialize
        response_data = {
            'message': f'Information for user with id {user_id}',
            'data': {
                'user': user_data,
                'projects': serializer.data
            }
        }

        return Response(response_data, status=status.HTTP_200_OK)


class UpdateProjectStatus(APIView):
    def post(self, request, project_id):
        try:
            # Lấy thông tin project với project_id
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({"message": "Project not found"}, status=status.HTTP_404_NOT_FOUND)

        # Lấy dữ liệu mới từ yêu cầu PUT
        new_status = request.data.get('status', None)

        if new_status is None:
            return Response({"message": "Status is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Cập nhật trạng thái
        project.status = new_status
        project.save()

        # Serialize thông tin đã cập nhật
        serializer = ProjectSerializer(project)

        response_data = {
            'message': 'Project status updated successfully',
            'data': serializer.data
        }

        return Response(response_data, status=status.HTTP_200_OK)


class UpdateProject(APIView):
    def put(self, request):
        # Lấy dữ liệu từ yêu cầu PUT
        project_data = request.data

        try:
            # Lấy thông tin project với project_id
            project_id = project_data.get('id')
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({"message": "Project not found"}, status=status.HTTP_404_NOT_FOUND)

        # Cập nhật thông tin project
        project.status = project_data.get('status', project.status)
        project.link_drive = project_data.get('linkDrive', project.link_drive)
        project.save()

        # Serialize thông tin đã cập nhật
        serializer = ProjectSerializer(project)

        response_data = {
            'message': 'Project updated successfully',
            'data': serializer.data
        }

        return Response(response_data, status=status.HTTP_200_OK)


class UserDataManageAPI(APIView):
    def get(self, request):
        # Ottieni tutti gli utenti
        users = User.objects.all()

        # Creare una lista per memorizzare i dati dell'utente e i relativi progetti
        data_list = []

        for user in users:
            # Serializza le informazioni sull'utente
            user_serializer = UserSerializer(user)

            # Ottieni i progetti associati all'utente corrente
            projects = Project.objects.filter(user=user)
            project_serializer = ProjectSerializer(projects, many=True)

            # Crea il dato dell'utente e i relativi progetti
            user_data = {
                "user": user_serializer.data,
                "projects": project_serializer.data
            }

            # Aggiungi il dato dell'utente alla lista
            data_list.append(user_data)

        # Creare la risposta JSON
        response_data = {
            "message": "Get data user manage project successful",
            "data": data_list
        }

        return Response(response_data, status=status.HTTP_200_OK)


class GetUserFromProjectView(APIView):
    def get(self, request, id):
        # Retrieve the project based on the given ID or return a 404 if not found
        project = get_object_or_404(Project, id=id)

        # Get the user for the project
        user = project.user

        # Serialize the user data
        user_serializer = UserSerializer(user)

        # Return the serialized user data along with the user ID
        response_data = {
            'user_id': user.id if user else None,
            'user_info': user_serializer.data if user else None
        }

        return Response(response_data)


class UserInfoAPI(APIView):
    def get(self, request):
        # Kiểm tra người dùng đã đăng nhập hay chưa
        if request.user.is_authenticated:
            user_data = UserSerializer(request.user).data
            return Response({'user': user_data}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'User is not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)


class UpdateUserInfoAPI(APIView):
    def put(self, request):
        user_id = request.data.get('id')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            # Lấy thông tin người dùng sau cập nhật
            updated_user = User.objects.get(id=user_id)
            updated_user_data = UserSerializer(updated_user).data
            return Response({'message': 'User information updated successfully', 'user': updated_user_data}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPI(APIView):
    def post(self, request):
        try:
            # Đăng xuất người dùng bằng cách xóa token
            request.auth.delete()
            return Response({'message': 'User logged out successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': 'Logout failed', 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class GetUserByIDAPI(APIView):
    def get(self, request, user_id):
        try:
            # Lấy thông tin người dùng với user_id
            user = get_object_or_404(User, id=user_id)

            # Lấy thông tin tất cả các dự án của người dùng
            projects = Project.objects.filter(user=user)
            project_serializer = ProjectSerializer(projects, many=True)

            # Serialize thông tin người dùng
            user_serializer = UserSerializer(user)

            # Tạo response chứa thông tin đã được serialize
            response_data = {
                'message': f'Thông tin người dùng với id {user_id}',
                'data': {
                    'user': user_serializer.data,
                    'projects': project_serializer.data
                }
            }

            return Response(response_data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'message': 'Không tìm thấy người dùng với ID đã cung cấp'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': 'Lấy thông tin người dùng thất bại', 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class GetUserByNameAPI(APIView):
    def get(self, request, username):
        try:
            # Lấy thông tin người dùng với username
            user = get_object_or_404(User, username=username)

            # Lấy thông tin tất cả các dự án của người dùng
            projects = Project.objects.filter(user=user)
            project_serializer = ProjectSerializer(projects, many=True)

            # Serialize thông tin người dùng
            user_serializer = UserSerializer(user)

            # Tạo response chứa thông tin đã được serialize
            response_data = {
                'message': f'Thông tin người dùng với tên người dùng {username}',
                'data': {
                    'user': user_serializer.data,
                    'projects': project_serializer.data
                }
            }

            return Response(response_data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'message': 'Không tìm thấy người dùng với tên người dùng đã cung cấp'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': 'Lấy thông tin người dùng thất bại', 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DeleteUserAPI(APIView):
    def delete(self, request, user_id):
        try:
            # Lấy người dùng dựa trên user_id
            user = get_object_or_404(User, id=user_id)

            # Lấy thông tin tất cả các dự án của người dùng
            projects = Project.objects.filter(user=user)
            project_serializer = ProjectSerializer(projects, many=True)

            # Serialize thông tin người dùng
            user_serializer = UserSerializer(user)

            # Xóa tài khoản người dùng
            user.delete()

            # Tạo response chứa thông tin đã được serialize và thông tin về xóa
            response_data = {
                'message': 'Xóa tài khoản người dùng thành công',
                'deleted_user': user_serializer.data,
                'deleted_projects': project_serializer.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'message': 'Không tìm thấy người dùng với ID đã cung cấp'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': 'Xóa tài khoản người dùng thất bại', 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Tải mô hình và đặt là biến toàn cục
model_path = '/Users/letiendat/Desktop/PBL6/docker-cnn/model/bike_car.h5'
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
