from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('<int:movie.pk>/', views.detail),
    path('<int:movie.pk>/review/<int:review.pk>/likes/<int:user.pk>/', views.likes),
    path('<int:movie.pk>/ticketing/<int:user.pk>/', views.ticketing),
    path('worldcup/', views.worldcup),
]