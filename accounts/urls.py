from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login),
    # path('<int:user.pk>/logout/', views.logout),
    path('signup/', views.signup),
    # path('<int:user.pk>/delete/', views.delete),
    # path('<int:user.pk>/profile/', views.profile),
]