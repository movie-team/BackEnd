from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from . import views

urlpatterns = [
    path('login/', views.login),
    # path('<int:user.pk>/logout/', views.logout),
    path('signup/', views.signup),
    # jwt 토큰 재발급
    path('auth/refresh/', TokenRefreshView.as_view()),
    path('auth/verify', TokenVerifyView.as_view()),
    path('test/', views.test)
    # path('<int:user.pk>/delete/', views.delete),
    # path('<int:user.pk>/profile/', views.profile),
]