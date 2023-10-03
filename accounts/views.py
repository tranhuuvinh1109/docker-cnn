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
        serializer = ProjectSerializer(data=request.data)

        if serializer.is_valid():
            # Save the project
            project = serializer.save()

            # Retrieve the serialized user data
            user_data = UserSerializer(project.user).data

            # Update the serialized data with user information
            response_data = {
                'message': 'Project created successfully',
                'data': {
                    'id': project.id,
                    'user': user_data,
                    'progress': project.progress,
                    'status': project.status,
                    'link_drive': project.link_drive
                }
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            response_data = {
                'message': 'Project creation failed',
                'errors': serializer.errors
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


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
