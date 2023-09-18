from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

def upload_file_to_drive(file_path):
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()  # Mở cửa sổ trình duyệt để xác thực

    drive = GoogleDrive(gauth)

    # Tạo một tệp mới trên Google Drive
    file_drive = drive.CreateFile({'title': 'my_file.zip'})

    # Thiết lập đường dẫn của tệp tin cần upload
    file_drive.SetContentFile(file_path)

    # Upload tệp tin lên Google Drive
    file_drive.Upload()

    print('Tệp tin đã được tải lên thành công:', file_drive['title'])

# Sử dụng hàm để upload tệp tin
upload_file_to_drive('path_to_your_zip_file.zip')