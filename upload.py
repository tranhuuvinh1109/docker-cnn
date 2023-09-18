from django.shortcuts import render
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

def upload_folder(request):
    if request.method == 'POST':
        # Khởi tạo xác thực Google Drive API
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()

        # Tạo kết nối tới Google Drive
        drive = GoogleDrive(gauth)

        # Thư mục bạn muốn upload lên Google Drive
        folder_path = '/path/to/your/folder'

        # Tạo một thư mục mới trên Google Drive
        folder = drive.CreateFile({'title': 'My Folder', 'mimeType': 'application/vnd.google-apps.folder'})
        folder.Upload()

        # Upload các tệp trong thư mục cục bộ vào thư mục trên Google Drive
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            file_drive = drive.CreateFile({'title': filename, 'parents': [{'id': folder['id']}]})
            file_drive.Upload()

    return render(request, 'upload.html')

