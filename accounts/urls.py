from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from . import views

urlpatterns = [
    path('login/', views.login),
    path('logout/', views.logout),
    path('signup/', views.signup),
    # jwt 토큰 재발급
    path('auth/refresh/', TokenRefreshView.as_view()),
    # jwt 토큰 유효성 진단
    path('auth/verify/', TokenVerifyView.as_view()),

    path('signout/', views.signout),
    path('update/', views.update),
    path('password/', views.password),
    path('', views.profile),

    # 비밀번호 찾기 api
    path('password/reset/', views.rest_password),
    path('password/reset/confirm/', views.rest_password_confirm),

    # 회원가입 시 이메일 인증
    path('confirm/', views.confirm),
    path('emailVerify/', views.verify_email),

]