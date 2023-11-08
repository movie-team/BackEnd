from django.shortcuts import get_list_or_404, get_object_or_404
from .models import User
from .serializers import UserSerializer
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
# JWT 토큰 검증 모듈
from rest_framework.permissions import IsAuthenticated
# Create your views here.

# 회원가입
@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()
        
        # jwt 토큰 접근
        token = TokenObtainPairSerializer.get_token(user)
        refresh_token = str(token)
        access_token = str(token.access_token)
        response = Response(
            {
                'user': serializer.data,
                'message': 'signup successs',
                'token': {
                    'access': access_token,
                    'refresh': refresh_token,
                },
            },
            status=status.HTTP_200_OK,
        )
        
        # jwt 토큰 쿠키에 저장
        response.set_cookie('access', access_token, httponly=True)
        response.set_cookie('refresh', refresh_token, httponly=True)
        
        return response
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):
    # 유저 인증
    user = authenticate(
        email=request.data.get('email'), password=request.data.get('password')
    )
    
    if user is not None:
        serializer = UserSerializer(user)
        # jwt 토큰 접근
        token = TokenObtainPairSerializer.get_token(user)
        refresh_token = str(token)
        access_token = str(token.access_token)
        res = Response(
            {
                'user': serializer.data,
                'message': 'login success',
                'token': {
                    'access': access_token,
                    'refresh': refresh_token,
                },
            },
            status=status.HTTP_200_OK,
        )
        # jwt 토큰 쿠키에 저장
        res.set_cookie('access', access_token, httponly=True)
        res.set_cookie('refresh', refresh_token, httponly=True)
        return res
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)

# jwt 토큰 인증 후 사용 가능한 서비스 테스트
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def test(request):
    User = get_user_model()
    accounts = get_list_or_404(User)
    serializer = UserSerializer(accounts, many=True)
    return Response(serializer.data)