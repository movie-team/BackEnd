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
    path('auth/verify', TokenVerifyView.as_view()),

    path('signout/', views.signout),
    path('update/', views.update),
    path('password/', views.password),
    path('', views.profile),

]