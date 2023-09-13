FROM python:3.10

ENV PYTHONUNBUFFERED=1

WORKDIR /code

COPY requirements.txt .

# Cập nhật pip và cài đặt các thư viện phụ thuộc
RUN pip install --upgrade pip
RUN apt-get update && apt-get install -y cmake

# Cài đặt các package Python
RUN pip install -r requirements.txt

# Cài đặt dlib
RUN pip install dlib

COPY . .

EXPOSE 8000

CMD ["python","manage.py","runserver"]