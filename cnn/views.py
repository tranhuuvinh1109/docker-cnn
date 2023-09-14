from rest_framework.decorators import api_view
from rest_framework .response import Response

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .serializers import UserSerializer
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

from django.shortcuts import get_object_or_404

@api_view(['POST'])
def login(request):
    user = get_object_or_404(User, email=request.data['email'])
    if not user.check_password(request.data['password']):
        return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)
    token, created = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(user)
    return Response({'token': token.key, "user": serializer.data})


@api_view(['POST'])
def signup(request):
    email = request.data.get('email')
    password = request.data.get('password')
    username = request.data.get('email')

    if not email or not password:
        return Response({'error': 'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Kiểm tra xem đã tồn tại tài khoản với email này chưa
    if User.objects.filter(email=email).exists():
        return Response({'error': 'This email is already in use.'}, status=status.HTTP_400_BAD_REQUEST)

    # Tạo một tài khoản mới
    user = User.objects.create_user(email=email, password=password, username=email)

    # Tạo token cho tài khoản
    token, created = Token.objects.get_or_create(user=user)

    return Response({'token': token.key, 'user': UserSerializer(user).data})

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    return Response("passed! for {}".format(request.user.username))