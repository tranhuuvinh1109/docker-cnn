
from django.urls import path
from upload import views

urlpatterns = [
    path("upload", views.upload_folder),
    path("success", views.success),
    path('authenticate', views.authenticate_google_drive, name='authenticate_google_drive')

]