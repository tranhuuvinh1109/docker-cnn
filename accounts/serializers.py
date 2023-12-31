# from rest_framework import serializers
# from .models import *


# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ('id', 'email', 'password', 'avatar', 'username')
#         extra_kwargs = {'password': {'write_only': True}}

#     def create(self, validated_data):
#         user = User.objects.create_user(
#             email=validated_data['email'],
#             avatar=validated_data['avatar'],
#             password=validated_data['password'],
#             username=validated_data['username']
#         )
#         return user


# class VerifyAccountSerializer(serializers.Serializer):
#     email = serializers.EmailField(required=True)
#     otp = serializers.CharField(required=True)


# class LoginSerializer(serializers.Serializer):
#     email = serializers.EmailField(required=True)
#     password = serializers.CharField(required=True)

#     class Meta:
#         model = User
#         fields = ('email', 'password')
#         extra_kwargs = {'password': {'write_only': True}}


# class ProjectSerializer(serializers.ModelSerializer):

#     # user = UserSerializer()  # Use the UserSerializer to serialize the user field

#     class Meta:
#         model = Project
#         fields = ['id', 'user', 'progress', 'status', 'link_drive']
from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'avatar', 'username')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            avatar=validated_data['avatar'],
            password=validated_data['password'],
            username=validated_data['username']
        )
        return user


class VerifyAccountSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('email', 'password')
        extra_kwargs = {'password': {'write_only': True}}


class ProjectSerializer(serializers.ModelSerializer):

    # user = UserSerializer()  # Use the UserSerializer to serialize the user field

    class Meta:
        model = Project
        fields = ['id', 'user', 'name' , 'progress', 'status', 'link_drive']