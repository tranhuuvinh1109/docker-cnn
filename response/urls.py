
from django.urls import path
from response import views

urlpatterns = [
    path("response", views.Reponse.as_view()),

]