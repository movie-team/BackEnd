from django.urls import path
from . import views
app_name = 'movies'

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:movie.pk>/', views.detail, name='detail'),
    path('review/<int:review.pk>/likes/', views.likes, name='likes'),
    path('<int:movie.pk>/ticketing/', views.ticketing, name='ticketing'),
    path('worldcup/', views.worldcup, name='worldcup'),
]