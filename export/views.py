import os
import rarfile
from rarfile import RarFile
from rest_framework.response import Response

rarfile.UNRAR_TOOL = r"C:/Program Files/WinRAR/UnRAR.exe"

def unrar(file, destination):
    rf = rarfile.RarFile(file)
    rf.extractall(destination)

class UploadAndUnzip():
    def unzipFile(rar_file, project_id):        
        # Xác định thư mục để lưu trữ các tệp giải nén
        destination_dir = 'D:/Django/CNN/docker-cnn/datasets/'

        # Tạo thư mục nếu nó không tồn tại
        os.makedirs(destination_dir, exist_ok=True)

        # Tạo thư mục project_id
        project_dir = os.path.join(destination_dir, project_id)
        os.makedirs(project_dir, exist_ok=True)

        # Lưu trữ tệp RAR tải lên
        rar_file_path = os.path.join(destination_dir, project_id + '.rar')

        with open(rar_file_path, 'wb+') as destination:
            for chunk in rar_file.chunks():
                destination.write(chunk)
        
        try:
            unrar(rar_file_path, project_dir)
        except:
            return 0
        
        # Xóa file rar vừa tải về máy
        if os.path.exists(rar_file_path):
            os.remove(rar_file_path)
            print('Da duoc xoa')
        else:
            print('Loi xay ra')
            return 0
        
        return 1
