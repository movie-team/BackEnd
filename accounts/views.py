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
# refresh_token 객체 생성
from rest_framework_simplejwt.tokens import RefreshToken

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

# 회원 삭제
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def signout(request):
    user = request.user
    
    # 유저 삭제
    user.delete()
    
    # 유저의 토큰을 블랙리스트에 추가
    refresh_token = request.COOKIES.get('refresh')
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
        # 쿠키에서 토큰 삭제
        response = Response({
            "message": "signout success"
        }, status=status.HTTP_200_OK)

        response.delete_cookie('access')
        response.delete_cookie('refresh')

        return response
    except Exception as e:
        return Response({'message': str(e)}, status=500)

# 로그인
@api_view(['POST'])
def login(request):
    # 유저 인증
    user = authenticate(
        email=request.data.get('email'), password=request.data.get('password')
    )
    User = get_user_model()
    print(User.objects.get(email=request.data.get('email')))

    print(user)
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

# 로그아웃    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    refresh_token = request.COOKIES.get('refresh')
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()  # 블랙리스트에 추가하여 해당 토큰으로 접근 불가
        response = Response({
            "message": "Logout success"
        }, status=status.HTTP_202_ACCEPTED)

        response.delete_cookie("access")
        response.delete_cookie("refresh") # 쿠키에서 해당 토큰 삭제

        return response
    except Exception as e:
        return Response({'message': str(e)}, status=500)
    
# 유저 정보 변경    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update(request):
    User = get_user_model()
    user = User.objects.get(email=request.user.email)
    serializer = UserSerializer(user, data=request.data)

    if serializer.is_valid():
        serializer.save()

        response = Response(
            {
                'user': serializer.data,
                'message': 'update successs',
            },
            status=status.HTTP_200_OK,
        )

        return response
    
    return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)


# 비밀번호 변경
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def password(request):
    new_password = request.data.get('password')
    
    try:
        # JWT 토큰 재설정
        token = TokenObtainPairSerializer.get_token(request.user)
        refresh_token = str(token)
        access_token = str(token.access_token)
        # 새로운 비밀번호 설정
        request.user.set_password(new_password)
        request.user.save()


        response = Response(
            {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'message': 'Password changed successfully.'
            }
        )

        return response

    except Exception as e:
        response = Response(
            {
                'message': 'Failed to change password.', 
                'error': str(e)
            }, 
            status=status.HTTP_400_BAD_REQUEST
        )

        return response
    

# 사용자 정보 제공
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    User = get_user_model()
    user = get_object_or_404(User, email=request.user.email)
    serializer = UserSerializer(user)
    return Response(serializer.data)