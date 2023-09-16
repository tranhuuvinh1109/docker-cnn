from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'is_verified')
        extra_kwargs = {'password': {'write_only': True}}
    def create(self, validated_data):   
        user = User.objects.create_user(validated_data['email'], validated_data['password'])
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