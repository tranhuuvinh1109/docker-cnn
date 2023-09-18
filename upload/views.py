from django.shortcuts import render

# Create your views here.

from django.http import JsonResponse

import tempfile


# ham dung de lay link json google oauth
from django.shortcuts import render
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os

import json



base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
json_filepath = os.path.join(base_dir, 'document', 'client_secret.json')


def authenticate_with_google_drive(client_secrets_path):
    gauth = GoogleAuth()
    gauth.LoadClientConfigFile(client_secrets_path)
    gauth.LocalWebserverAuth()
    return gauth


import tempfile
#xu li up file zip
def upload_folder(request):
    if request.method == 'POST' and request.FILES['file']:
        # Xac nhan google drive api
        gauth = authenticate_with_google_drive(json_filepath)
        gauth.LocalWebserverAuth()

        # ket noi google
        drive = GoogleDrive(gauth)

        # up file
        file_to_upload = request.FILES['file']

        # kt la file zip
        if not file_to_upload.name.endswith('.zip'):
            return JsonResponse({'status': 'Only zip files are allowed.'}, status=400)

        # chuyen the binary
        file_content = file_to_upload.read()

    #up file
        # Create a temporary zip file to upload to Google Drive
        temp_zip_file = tempfile.NamedTemporaryFile(suffix='.zip', delete=False)
        temp_zip_file.write(file_content)
        temp_zip_file.close()

        # Create a new file on Google Drive and set the content from the uploaded zip file
        file_drive = drive.CreateFile({'title': file_to_upload.name})
        file_drive.SetContentFile(temp_zip_file.name)  # Set content from the temporary zip file
        file_drive.Upload()

        
        # tao link
        file_drive.InsertPermission({
            'type': 'anyone',
            'value': 'anyone',
            'role': 'reader'
        })


        
        # lay link
        file_link = file_drive['alternateLink']
        print('Đây là liên kết chia sẻ tới file:', file_link)

        
        # zoa flie zip tam
        os.unlink(temp_zip_file.name)

        return JsonResponse({'status': 'File uploaded successfully.'})

    return render(request, 'upload/upload.html')
    



# def upload_folder(request):
#     if request.method == 'POST' and request.FILES['file']:
#         # Get the uploaded file
#         file_to_upload = request.FILES['file']

#         # Ensure it's a PNG file
#         try:
#             img = Image.open(file_to_upload)
#             if img.format != 'PNG':
#                 return JsonResponse({'status': 'Only PNG files are allowed.'}, status=400)
#         except:
#             return JsonResponse({'status': 'Invalid image format.'}, status=400)

#         # Initialize Google Drive API authentication
#         gauth = authenticate_with_google_drive(json_filepath)
#         gauth.LocalWebserverAuth()

#         # Create a connection to Google Drive
#         drive = GoogleDrive(gauth)

#         # Read the binary content of the file
#         file_content = file_to_upload.read()

#         # Create a temporary PNG file to upload to Google Drive
#         temp_png_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
#         temp_png_file.write(file_content)
#         temp_png_file.close()

#         # Create a new file on Google Drive and set the content from the uploaded PNG file
#         file_drive = drive.CreateFile({'title': file_to_upload.name})
#         file_drive.SetContentFile(temp_png_file.name)  # Set content from the temporary PNG file
#         file_drive.Upload()

#         # Delete the temporary PNG file
#         os.unlink(temp_png_file.name)

#         return JsonResponse({'status': 'File uploaded successfully.'})

#     return render(request, 'upload/upload.html')





# text
# # @csrf_exempt
# def upload_folder(request):
#     if request.method == 'POST' and request.FILES['file']:
#         # Khởi tạo xác thực Google Drive API
#         gauth = authenticate_with_google_drive(json_filepath)

#         gauth.LocalWebserverAuth()

#         # Tạo kết nối tới Google Drive
#         drive = GoogleDrive(gauth)

#         # Tệp bạn muốn upload lên Google Drive
#         file_to_upload = request.FILES['file']

#         # Tạo một tệp mới trên Google Drive và đặt nội dung từ tệp được gửi lên
#         file_drive = drive.CreateFile({'title': file_to_upload.name})
#         file_drive.SetContentString(file_to_upload.read())  # Đặt nội dung từ file

#         # Tải lên Google Drive
#         file_drive.Upload()

#         return JsonResponse({'status': 'File uploaded successfully.'})

#     return render(request, 'upload/temaplupload.html')
