"""PJT URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import getUserInfo, kakaoGetLogin, kakaoRefresh, kakaoLogout, kakaoSignout

urlpatterns = [
    path('admin/', admin.site.urls),
    # 사용자 관련 api 경로
    path('api/', include('accounts.urls')),
    # 카카오 소셜 로그인 경로
    path('accounts/kakao/login/', kakaoGetLogin),
    path('accounts/kakao/login/callback/', getUserInfo),
    path('accounts/kakao/refresh/', kakaoRefresh),
    path('accounts/kakao/logout/', kakaoLogout),
    path('accounts/kakao/signout/', kakaoSignout),
    # 영화 관련 api 경로
    path('api/movies/', include('movies.urls')),
    # 정적 파일 설정
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)