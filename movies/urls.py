from django.urls import path
from . import views
app_name = 'movies'

urlpatterns = [
    # 영화 정보 받아오기
    path('', views.movie_list, name='index'),
    path('<int:movie_pk>/', views.movie_detail, name='detail'),

    # 리뷰 api
    path('<str:username>/<int:movie_pk>/', views.review_create),


    path('review/<int:review_pk>/likes/', views.review_likes, name='likes'),
    # path('<int:movie.pk>/ticketing/', views.ticketing, name='ticketing'),
    # path('worldcup/', views.worldcup, name='worldcup'),\


    # 삭제 예정
    path('add/', views.add_data, name='add'),
    path('add/genres/', views.add_genres, name='add_genres'),
]