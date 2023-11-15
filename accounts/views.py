from django.shortcuts import get_list_or_404, get_object_or_404, redirect
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
# 비밀번호 비교 모듈
from django.contrib.auth.hashers import check_password

from rest_framework.permissions import AllowAny
from PJT.settings import SOCIAL_OUTH_CONFIG
import requests

# 회원가입
@api_view(['POST'])
@permission_classes([AllowAny, ])
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
@api_view(['DELETE'])
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
@permission_classes([AllowAny, ])
def login(request):
    # 유저 인증
    
    User = get_user_model()
    user = User.objects.get(username=request.data.get('username'))

    if user is not None:
        if check_password(request.data.get('password'), user.password):
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
            return Response({'message': 'wrong password'}, status=status.HTTP_400_BAD_REQUEST)
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
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update(request):
    User = get_user_model()
    user = User.objects.get(username=request.user.username)
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
@api_view(['PUT'])
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
@permission_classes([AllowAny, ])
@permission_classes([IsAuthenticated])
def profile(request):
    User = get_user_model()
    user = get_object_or_404(User, username=request.user.username)
    serializer = UserSerializer(user)
    return Response(serializer.data)


# 카카오 소셜 로그인 코드
# 1. 인가 코드 요청 후 리다이렉트
@api_view(['GET'])
@permission_classes([AllowAny, ])
def kakaoGetLogin(request):
    CLIENT_ID = SOCIAL_OUTH_CONFIG['KAKAO_REST_API_KEY']
    REDIRET_URL = SOCIAL_OUTH_CONFIG['KAKAO_REDIRECT_URI']
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRET_URL}&response_type=code"
    )

# 2. 인가 코드 기반 토큰 요청
# 3. 토큰 발급 후 토큰 기반 카카오 회원 정보 확인
# 4. 확인된 회원 정보로 회원 생성
@api_view(['GET'])
@permission_classes([AllowAny, ])
def getUserInfo(request):
    CODE = request.query_params['code']
    url = "https://kauth.kakao.com/oauth/token"
    res = {
            'grant_type': 'authorization_code',
            'client_id': SOCIAL_OUTH_CONFIG['KAKAO_REST_API_KEY'],
            'redirect_url': SOCIAL_OUTH_CONFIG['KAKAO_REDIRECT_URI'],
            'client_secret': SOCIAL_OUTH_CONFIG['KAKAO_SECRET_KEY'],
            'code': CODE
        }
    headers = {
        'Content-type': 'application/x-www-form-urlencoded;charset=utf-8'
    }
    response = requests.post(url, data=res, headers=headers)
    tokenJson = response.json()
    userUrl = "https://kapi.kakao.com/v2/user/me"
    auth = "Bearer "+tokenJson['access_token']
    
    HEADER = {
        "Authorization": auth,
        "Content-type": "application/x-www-form-urlencoded;charset=utf-8"
    }
    res = requests.get(userUrl, headers=HEADER)
    
    KAKAO_USER_INFO = res.json()
    
    email = KAKAO_USER_INFO.get('kakao_account', {}).get('email')
    username = KAKAO_USER_INFO.get('kakao_account', {}).get('profile', {}).get('nickname')
    id = KAKAO_USER_INFO.get('id')

    User = get_user_model()

    try:
        user = User.objects.get(username=username)
        if user.social:
            refresh_token = str(tokenJson['refresh_token'])
            access_token = str(tokenJson['access_token'])
            data = {
                'username': username,
                'email': email,
                'password': str(id),
                'social': True
            }

            response = Response(
                    {
                        'message': 'login successs',
                        'token': {
                            'access': access_token,
                            'refresh': refresh_token,
                        },
                    },
                    status=status.HTTP_200_OK,
                )
            return response

    except User.DoesNotExist:
        data = {
            'username': username,
            'email': email,
            'password': str(id),
            'social': True
        }
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            
            # jwt 토큰 접근
            refresh_token = str(tokenJson['refresh_token'])
            access_token = str(tokenJson['access_token'])
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
        
    return Response(
            {
                'message': 'same username already exsists'
            },
            status=status.HTTP_400_BAD_REQUEST
        )

def kakaoRefresh(request):
    url = "https://kauth.kakao.com/oauth/token"
    res = {
            'grant_type': 'refresh_token',
            'client_id': SOCIAL_OUTH_CONFIG['KAKAO_REST_API_KEY'],
            'refresh_token': request.COOKIES.get('refresh'),
            'client_secret': SOCIAL_OUTH_CONFIG['KAKAO_SECRET_KEY']
        }
    headers = {
        'Content-type': 'application/x-www-form-urlencoded;charset=utf-8'
    }
    res = requests.post(url, data=res, headers=headers)
    
    return Response(res.json())

def kakaoLogout(request):
    url = "https://kapi.kakao.com/v1/user/logout"

    auth = "Bearer "+ request.COOKIES.get('refresh')
    
    HEADER = {
        "Authorization": auth,
        "Content-type": "application/x-www-form-urlencoded;charset=utf-8"
    }
    res = requests.POST(url, headers=HEADER)
    return res
