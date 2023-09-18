from rest_framework.decorators import api_view
from rest_framework .response import Response

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .serializers import UserSerializer
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

from django.shortcuts import get_object_or_404


from django.shortcuts import render
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os

import json

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
json_filepath = os.path.join(base_dir, 'document', 'client_secret.json')

@api_view(['POST'])
def login(request):
    user = get_object_or_404(User, username=request.data['username'])
    if not user.check_password(request.data['password']):
        return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)
    token, created = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(instance=user)
    return Response({'token': token.key, "user": serializer.data})


@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        user = User.objects.get(username=request.data['username'])
        user.set_password(request.data['password'])
        user.save()
        token = Token.objects.create(user=user)
        return Response({'token': token.key, "user": serializer.data})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    return Response("passed! for {}".format(request.user.username))


# def upload_folder(request):
#     if request.method == 'POST' and request.FILES['file']:
#         # Khởi tạo xác thực Google Drive API
#         gauth = GoogleAuth()
#         gauth.LocalWebserverAuth()

#         # Tạo kết nối tới Google Drive
#         drive = GoogleDrive(gauth)

#         # Tệp bạn muốn upload lên Google Drive
#         file_to_upload = request.FILES['file']

#         # Tạo một tệp mới trên Google Drive
#         file_drive = drive.CreateFile({'title': file_to_upload.name})
#         file_drive.Upload()

#         return render(request, 'upload.html')

#     return render(request, 'upload.html')

def authenticate_with_google_drive(client_secrets_path):
    gauth = GoogleAuth()
    gauth.LoadClientConfigFile(client_secrets_path)
    gauth.LocalWebserverAuth()
    return gauth





# @csrf_exempt
def upload_folder(request):
    if request.method == 'POST' and request.FILES['file']:
        # Khởi tạo xác thực Google Drive API
        gauth = authenticate_with_google_drive(json_filepath)

        gauth.LocalWebserverAuth()

        # Tạo kết nối tới Google Drive
        drive = GoogleDrive(gauth)

        # Tệp bạn muốn upload lên Google Drive
        file_to_upload = request.FILES['file']

        # Tạo một tệp mới trên Google Drive và đặt nội dung từ tệp được gửi lên
        file_drive = drive.CreateFile({'title': file_to_upload.name})
        file_drive.SetContentString(file_to_upload.read())  # Đặt nội dung từ file

        # Tải lên Google Drive
        file_drive.Upload()

        return JsonResponse({'status': 'File uploaded successfully.'})

    return render(request, 'upload.html')