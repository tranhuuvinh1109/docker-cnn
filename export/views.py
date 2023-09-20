from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import zipfile
import json
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import zipfile
import os


class UploadAndUnzip(APIView):
    def post(self, request):
        if request.method == "POST" and request.FILES.get("data"):
            zip_file = request.FILES["data"]
            

        # Xác định thư mục để lưu trữ các tệp giải nén
        destination_dir = 'D:/Django/CNN/docker-cnn/datasets'

        # Tạo thư mục nếu nó không tồn tại
        os.makedirs(destination_dir, exist_ok=True)

        # Lưu trữ tệp ZIP tải lên
        zip_file_path = os.path.join(destination_dir, zip_file.name)
        with open(zip_file_path, 'wb+') as destination:
            for chunk in zip_file.chunks():
                destination.write(chunk)
                
        # Giải nén file zip:
        

        return Response({'message': 'ZIP file uploaded and extracted successfully'})  
