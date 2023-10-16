import os
import rarfile
from rarfile import RarFile
from rest_framework.response import Response
from queue import Queue
import threading
from trainModel import views as TrainModelViews
import scipy

rarfile.UNRAR_TOOL = r"C:/Program Files/WinRAR/UnRAR.exe"
# Xác định thư mục để lưu trữ các tệp giải nén
destination_dir = 'D:/Django/CNN/docker-cnn/datasets/'
temp_queue = []

def unrar(file, destination):
    rf = rarfile.RarFile(file)
    rf.extractall(destination)
trainer = TrainModelViews.TrainModel()  # Tạo một đối tượng TrainModel


class UnzipThread(threading.Thread):
    def run(self):
        while True:
            rar_file, project_id = unzip_queue.get()
            print(f"Unzipping project {project_id}...")
            try:
                # Đảm bảo chỉ một luồng giải nén tại một thời điểm
                with unzip_lock:
                    unrar(rar_file, destination_dir+project_id)
                    # base_data_dir
                    base_data_dir = destination_dir 
                    print('export path => .....', base_data_dir + project_id)
                    os.remove(rar_file)
                    if temp_queue:
                        temp_queue.pop(0)
                    export_dir=project_id
                    trainer.start_training(export_dir=export_dir)
                    for temp_item in temp_queue:
                        temp_rar_file, temp_project_id = temp_item
                        unrar(temp_rar_file, destination_dir + temp_project_id)
                    
                unzip_queue.task_done()
                
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
