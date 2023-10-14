import os
import rarfile
from rarfile import RarFile
from rest_framework.response import Response
from queue import Queue
import threading

rarfile.UNRAR_TOOL = r"C:/Program Files/WinRAR/UnRAR.exe"
# Xác định thư mục để lưu trữ các tệp giải nén
destination_dir = 'D:/Django/CNN/docker-cnn/datasets/'
def unrar(file, destination):
    rf = rarfile.RarFile(file)
    rf.extractall(destination)

class UnzipThread(threading.Thread):
    def run(self):
        while True:
            rar_file, project_id = unzip_queue.get()
            print(f"Unzipping project {project_id}...")
            try:
                # Đảm bảo chỉ một luồng giải nén tại một thời điểm
                with unzip_lock:
                    unrar(rar_file, destination_dir+project_id)
                    
                    
                unzip_queue.task_done()
                
                # if task done then delete folder .rar
                os.remove(rar_file)
                print(f"Unzipped project {project_id}")
                
            except Exception as e:
                print(f'Failed to extract RAR file for project {project_id}: {str(e)}')

unzip_queue = Queue()
unzip_lock = threading.Lock()  # Khóa để đảm bảo tính đồng bộ trong quá trình giải nén
num_worker_threads = 1

class UploadAndUnzip():
    def unzipFile(rar_file, project_id):

        # Tạo thư mục nếu nó không tồn tại
        os.makedirs(destination_dir, exist_ok=True)

        # Tạo thư mục project_id bên trong thư mục datasets
        project_dir = os.path.join(destination_dir, project_id)
        os.makedirs(project_dir, exist_ok=True)

        # Lưu trữ tệp RAR tải lên
        rar_file_path = os.path.join(project_dir, project_id + '.rar')

        with open(rar_file_path, 'wb+') as destination:
            for chunk in rar_file.chunks():
                destination.write(chunk)
        
        # Đưa tệp RAR và ID dự án vào hàng đợi để xử lý
        unzip_queue.put((rar_file_path, project_id))

        return 1

# Khởi tạo và chạy worker (tiến trình con) với các thread
for i in range(num_worker_threads):
    worker = UnzipThread()
    worker.daemon = True  # Đảm bảo thread dừng khi chương trình chính kết thúc
    worker.start()
