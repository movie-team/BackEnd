from django.urls import path
from . import views
app_name = 'movies'

urlpatterns = [
    path('', views.movie_list, name='index'),
    path('<int:movie_pk>/', views.movie_detail, name='detail'),
    # path('review/<int:review.pk>/likes/', views.likes, name='likes'),
    # path('<int:movie.pk>/ticketing/', views.ticketing, name='ticketing'),
    # path('worldcup/', views.worldcup, name='worldcup'),\
    path('add/', views.add_data, name='add'),
    path('add/genres/', views.add_genres, name='add_genres'),
]