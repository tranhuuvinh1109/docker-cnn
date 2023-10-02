from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import uuid
from .manager import UserManager


class User(AbstractUser):
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(
        max_length=254)
    is_verified = models.BooleanField(default=False)
    avatar = models.CharField(max_length=255)
    otp = models.CharField(max_length=6, null=True, blank=True)


class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    progress = models.IntegerField()
    status = models.CharField(max_length=255)
    link_drive = models.CharField(max_length=255)

    def __str__(self):
        return f"Project {self.id} - {self.status}"


class ForgetPassword(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    forget_password_token = models.CharField(
        max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email


'''  ALL SIGNALS HERE  '''
