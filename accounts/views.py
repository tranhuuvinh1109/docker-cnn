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
from trainModel import uploadToFirebase as uploadFB

from rest_framework.views import APIView
from rest_framework.response import Response
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload

# importing the zipfile module 
import zipfile
from django.contrib.auth import get_user_model
User = get_user_model()

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
        progress = 0
        status_text = 'waiting'
        link_drive = ''
        file = request.FILES.get("file")
        name = request.data.get("name")
        create_time = request.data.get('create_at')

        if file:
            print(">>>file name -->:", file.name)
        else:
            print("0000>>>file name -->:")
        # Tìm người dùng dựa trên user_id
        try:
            user = User.objects.get(id=user_id)
            print(">>>user -->:", user, file)
        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Tạo dự án mới với người dùng tìm được
        project = Project.objects.create(
            user=user, progress=progress, name=name, status=status_text, link_drive=link_drive)
        print("Project created -->0", project)
        # data_send = {
        #         'status': 'waiting',
        #         'progress': '0',
        #         'linkDrive': '',
        #         'createAt': create_time,
        #         'name':name
        #     }
        #     # create in firebase project user:
        # uploadFB.Firebase.setProject('user_1', project.id, data_send)

        # unzip file
        flagExport = export_views.UploadAndUnzip.unzipFile(
            file, 'project_' + str(project.id) + '-' + str(user_id))

        if flagExport == 1:
            data_send = {
                'status': 'waiting',
                'progress': '0',
                'linkDrive': '',
                'createAt': create_time,
                'name': name,
            }
            # create in firebase project user:
            uploadFB.Firebase.setProject(
                'user_'+user_id, project.id, data_send)
            serializer = ProjectSerializer(project)
            response_data = {
                'message': 'Project created successfully',
                'data': serializer.data
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'Error when unzip file'}, status=status.HTTP_400_BAD_REQUEST)
        # return Response({'message': 'Error when unzip file'}, status=status.HTTP_201_CREATED)


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


class Me(APIView):
    def post(self, request):
        # Lấy dữ liệu từ yêu cầu PUT
        user_id = request.data.get('user_id')

        try:
            user = User.objects.get(id=user_id)
        except Project.DoesNotExist:
            return Response({"message": "Project not found"}, status=status.HTTP_404_NOT_FOUND)

        response_data = {
            'message': 'Get Information successfully',
            'data': {
                'user': UserSerializer(user).data
            }
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


class UPLOAD_AUTO(APIView):
    def get(self, request):
        # Đường dẫn đến tệp JSON chứa thông tin Service Account Key
        SERVICE_ACCOUNT_FILE = '/Users/letiendat/Documents/Semes-Six/PBL6/docker-cnn/client_secrets.json'

        # Thiết lập phạm vi (scope)
        SCOPES = ['https://www.googleapis.com/auth/drive.file']

        # Tạo credentials từ Service Account File
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)

        # Khởi tạo dịch vụ Google Drive
        drive_service = build('drive', 'v3', credentials=credentials)

        # Đường dẫn tệp bạn muốn tải lên
        file_path = '/Users/letiendat/Documents/Semes-Six/PBL6/docker-cnn/requirements.txt'

        # Specify the folder ID where you want to upload the file
        folder_id = '1aAIkfZS-anf5E6M8uj5nUka5B8Iy4yQn'

        # Thực hiện tải lên tệp
        file_metadata = {
            'name': 'b.txt',
            'parents': [folder_id]
        }

        media = MediaFileUpload(file_path, mimetype='application/octet-stream')

        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        # Trả về thông báo thành công hoặc lỗi và URL của tệp
        if 'id' in file:
            file_id = file['id']
            file_url = "https://drive.google.com/file/d/" + file_id + "/view"
            # https://drive.google.com/file/d/15aZezP89eENIpUh5pQ-HjivtWXOj0uY_/view

            return Response({"message": "Upload success", "file_url": file_url})
        else:
            return Response({"error": "Upload failed"}, status=500)



class Train_Model(APIView):
    def get(self, request):
        file_path = ''
        file_name = 'model_new.h5'
        url = Upload_auto_drive(file_path,file_name )
        print('getttt')
        return Response({'message': 'ok', "url":url})
    def post(self, request):
        # file, user_id, project_id
        print("---->>POST<>>>>>>")
        user_id = request.data.get('user_id')
        project_id = request.data.get('project_id')
        file = request.FILES.get("file")
        name = request.data.get("name")
        create_time = request.data.get('create_at')

        if file:
            print(">>>file name -->:", file.name)
        else:
            print("0000>>>file name -->:")

        # unzip file
        flagExport = export_views.UploadAndUnzip.unzipFile(
            file, 'project_' + str(project_id) + '-' + str(user_id))

        if flagExport == 1:
            data_send = {
                'status': 'waiting',
                'progress': '0',
                'linkDrive': '',
                'createAt': create_time,
                'name': name,
            }
            # create in firebase project user:
            uploadFB.Firebase.updateProject(
                'user_'+user_id, project_id, data_send)
            
            return Response({"data": {
                "user_id": user_id,
                "project_id": project_id
            }}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'Error when unzip file'}, status=status.HTTP_400_BAD_REQUEST)


class Unzip(APIView):
    def get(self, request):
        file_path = 'F:/WORKS/MATERIALS/4th_year/LapTrinhMang/data_test/bikeCar.zip'
        extract_path = 'F:/WORKS/MATERIALS/4th_year/LapTrinhMang/data_test/unzip/'
        
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            print("Đã giải nén thành công.")
            return Response({"data": "Đã giải nén thành công."}, status=status.HTTP_201_CREATED)
        except zipfile.BadZipFile:
            print("Lỗi: Tệp ZIP không hợp lệ.")
            return Response({"error": "Lỗi: Tệp ZIP không hợp lệ."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Lỗi: {e}")
            return Response({"error": f"Lỗi: {e}"}, status=status.HTTP_400_BAD_REQUEST)
    
def Upload_auto_drive(file_path, file_name):
    print(">>>DANG UP NE>>>>")
    SERVICE_ACCOUNT_FILE = 'F:/WORKS/MATERIALS/4th_year/LapTrinhMang/docker-cnn/client_secrets.json'
    SCOPES = ['https://www.googleapis.com/auth/drive.file']

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    drive_service = build('drive', 'v3', credentials=credentials)


    folder_id = '1aAIkfZS-anf5E6M8uj5nUka5B8Iy4yQn'

    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }

    media = MediaFileUpload(file_path, mimetype='application/octet-stream')

    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    if 'id' in file:
        file_id = file['id']
        file_url = "https://drive.google.com/file/d/" + file_id + "/view"
        # https://drive.google.com/file/d/15aZezP89eENIpUh5pQ-HjivtWXOj0uY_/view

        return file_url
    else:
        return 0