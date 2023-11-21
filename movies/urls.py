from django.urls import path
from . import views
app_name = 'movies'

urlpatterns = [
    # 영화 정보 받아오기
    path('', views.movie_list),
    path('<int:movie_pk>/', views.movie_detail, name='detail'),
    path('genre/', views.genre),
    path('genre/<int:genre_pk>/', views.genre_movie, name='genre_movie'),
    path('popularity/', views.popular_movie, name='popular_movie'),
    # path('gender/', views.gender_movie, name='gender_movie'),
    # path('age/', views.age_movie, name='age_movie'),

    # 리뷰 api
    path('<int:movie_pk>/review/', views.review),
    path('<int:movie_pk>/reviewCreate/', views.review_create),
    path('<int:movie_pk>/<int:review_pk>/', views.review_control),
    path('<int:movie_pk>/user_group_rating/', views.user_group_rating),
    path('<int:movie_pk>/group_rating/', views.group_rating),


    path('review/<int:review_pk>/likes/', views.review_likes, name='likes'),
    # path('<int:movie.pk>/ticketing/', views.ticketing, name='ticketing'),
    
    # 추천 알고리즘
    path('<int:movie_pk>/genre_recommendation/', views.genre_recommend, name='genre_recommend'),
    path('worldcup/', views.worldcup, name='worldcup'),
    path('user_based_recommendation/', views.user_recommend, name='user_recommend'),

    # 상영관 당 좌석 상태
    path('theater/<int:theater_pk>/', views.theater_detail),

    # 티켓 관련 api
    # 티켓 생성
    path('ticket/', views.ticket_create),
    # 티켓 삭제 (좌석 별)
    path('ticket/<int:seat_pk>/', views.ticket_delete),
    # 티켓 결제 요청(카카오페이)
    path('ticket/pay/', views.ticket_pay),
    # 티켓 결제 완료
    path('success/', views.success),
    path('confirm/', views.payConfirm),
    path('cancel/', views.payCancel),

    # 삭제 예정
    # path('add/genres/', views.add_genres, name='add_genres'),
]