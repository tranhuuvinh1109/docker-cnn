
from django.urls import path
from upload import views

urlpatterns = [
    path("upload", views.upload_folder)
]