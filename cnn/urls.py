"""
URL configuration for cnn project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.contrib import admin
from accounts.views import *
from export.views import *
from trainModel.views import *

urlpatterns = [
    path('register/', RegisterAPI.as_view()),
    path('verify/', VerifyOTP.as_view()),
    path("admin/", admin.site.urls),
    path('login/', LoginAPI.as_view()),
    # path('unzip/', UploadAndUnzip.as_view()),

    path('create_project/', CreateProjectAPI.as_view(), name='create-project'),
    path('user_manage/<int:user_id>/', InforUser.as_view(), name='infor-user'),
    path('update_project_status/<int:project_id>/',
        UpdateProjectStatus.as_view(), name='update_project_status'),
    path('update_project/', UpdateProject.as_view(), name='update_project'),
    path('admin_manage/all_user/', UserDataManageAPI.as_view(),
        name='admin_manage/all_user'),
    
    path("trainModel/", TrainModelView.as_view()),
    # path('detect/', DetectImage.as_view(), name='detect-image'),
    path("", include("upload.urls")),
]
