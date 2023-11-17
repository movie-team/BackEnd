from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404, get_list_or_404
from django.contrib.auth import get_user_model
from .serializers import MovieSerializer, TestSerializer, GenreSerializer, ReviewSerializer, ReviewLikesSerializer, TheaterSerializer, SeatSerializer
from .models import Movie, Genre, Test_model, Review, Review_likes, Theater, Seat

from rest_framework import status

import requests
import json
from rest_framework.permissions import AllowAny, IsAuthenticated

from pprint import pprint
from time import sleep

from django.db.models import Avg

# Create your views here.

# 영화 전체 조회
@api_view(['GET',])
@permission_classes([AllowAny,])
def movie_list(request):
    if request.method == 'GET':
        movies = get_list_or_404(Movie)
        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data)

# 영화 상세 조회
@api_view(['GET',])
@permission_classes([AllowAny,])
def movie_detail(request, movie_pk):
    movie = get_object_or_404(Movie, id=movie_pk)
    if request.method == 'GET':
        serializer = MovieSerializer(movie)
        print(serializer.data)
        return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def genre(request):
    genre = get_list_or_404(Genre)
    serializer = GenreSerializer(genre, many=True)
    return Response(serializer.data)

# 장르 별 영화 추천
@api_view(['GET',])
@permission_classes([AllowAny,])
def genre_movie(request, genre_pk):
    print('genre_movie')
    movies = get_list_or_404(Movie, genres = genre_pk)
    serializer = MovieSerializer(movies, many=True)
    return Response(serializer.data)


# 인기도 별 영화 정렬
@api_view(['GET',])
@permission_classes([AllowAny,])
def popular_movie(request):
    movies = get_list_or_404(Movie.objects.order_by('-popularity'))
    serializer = MovieSerializer(movies, many=True)
    return Response(serializer.data)
            

# 장르 유사도 기반 추천 알고리즘
@api_view(['GET'])
@permission_classes([AllowAny,])
def genre_recommend(request, movie_pk):
    movie = get_object_or_404(Movie, id=movie_pk)
    movies = get_list_or_404(Movie.objects.order_by('-popularity'))

    # # popularity 중간값 및 분포 확인
    # median_popularity = movies[len(movies)//2].popularity
    # print(f'median: {median_popularity}')
    # for m in movies:
    #     print(m.popularity, end=' ')

    # 목표 유사도를 만족하는 인기도 최상위 영화 리스트를 반환하는 함수
    def similarity(genres, targets):
        genres_length = len(genres)
        similar_list = []

        target_similarity = 0.4 # 목표 유사도
        target_num_of_movies = 10 # 목표 영화 개수
        num_of_movie = 0
        for i, target in enumerate(targets):
            target_queryset = target.genres.all()
            count = 0
            for genre in genres:
                if genre in target_queryset:
                    count += 1
            if count/genres_length > target_similarity:
                similar_list.append(target)
                num_of_movie += 1
                if num_of_movie >= target_num_of_movies:
                    break
        return similar_list
    
    print('???',similarity(movie.genres.all(), movies))
    serializer = MovieSerializer(similarity(movie.genres.all(), movies), many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated,])
def user_group_rating(request, movie_pk):
    user_gender = request.user.gender
    user_age_group = (request.user.age//10)*10
    print(user_gender, user_age_group)
    reviews = Review.objects.filter(movie=movie_pk, user__gender=user_gender, user__age__gte=user_age_group, user__age__lt=user_age_group+10)
    rating = reviews.aggregate(Avg("rating"))
    print(reviews)
    print(rating)
    rating['gender'] = user_gender
    rating['age_group'] = user_age_group
    return Response(rating)


@api_view(['GET'])
@permission_classes([AllowAny,])
def group_rating(request, movie_pk):
    genders = [ True, False ]
    age_groups = [10, 20, 30, 40, 50]
    rating_list = []
    for gender in genders:
        for age_group in age_groups:
            if age_group == 10:
                reviews = Review.objects.filter(movie=movie_pk, user__gender=gender, user__age__lt=age_group+10)
            elif age_group == 50:
                reviews = Review.objects.filter(movie=movie_pk, user__gender=gender, user__age__gte=age_group)
            else:
                reviews = Review.objects.filter(movie=movie_pk, user__gender=gender, user__age__gte=age_group, user__age__lt=age_group+10)
            group = reviews.aggregate(Avg("rating"))
            group['gender'] = gender
            group['age_group'] = age_group
            rating_list.append(group)
    return Response(rating_list)

@api_view(['GET'])
@permission_classes([AllowAny,])
def review(request, movie_pk):
    movie = get_object_or_404(Movie, id=movie_pk)
    reviews = movie.review_set.all()
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)


# 리뷰 생성
# 영화 당 사용자는 리뷰 한 개만 작성 가능
@api_view(['POST'])
@permission_classes([IsAuthenticated, ])
def review_create(request, movie_pk):
    movie = get_object_or_404(Movie, id=movie_pk)
    user = request.user

    try:
        Review.objects.get(movie=movie, user=user)
        return Response(
            {
                'message': 'you already wrote review'
            },
            status = status.HTTP_400_BAD_REQUEST
        )

    except Review.DoesNotExist:
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            origin_rating = movie.vote_average
            origin_nums = movie.vote_count
            user_rating = float(request.data['rating'])
            
            new_rating = origin_rating*origin_nums+user_rating
            new_nums = origin_nums+1

            movie.vote_average = round(new_rating / new_nums,  1)
            movie.vote_count = new_nums
            movie.save()


            serializer.save(movie=movie, user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    


# 리뷰 수정 및 삭제
@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated, ])
def review_control(request, movie_pk, review_pk):
    user = request.user
    review = Review.objects.get(pk=review_pk)
    movie = get_object_or_404(Movie, id=movie_pk)
    origin_rating = movie.vote_average
    origin_nums = movie.vote_count

    check_user = review.user_id

    if user.id == check_user:
        if request.method == 'PUT':
            serializer = ReviewSerializer(review, data=request.data)
            if serializer.is_valid():
                if(request.data['rating'] != review.rating):
                    new_rating = origin_rating*origin_nums-review.rating+request.data['rating']
                
                    movie.vote_average = round(new_rating / origin_nums,  1)
                    
                    movie.save()

                serializer.save()
                return Response(serializer.data)

        elif request.method == 'DELETE':
            new_rating = origin_rating*origin_nums-review.rating
            new_nums = origin_nums-1

            movie.vote_average = round(new_rating / new_nums,  1)
            
            movie.save()

            review.delete()
            return Response(
                {
                    "message": "delete success"
                },
                status = status.HTTP_204_NO_CONTENT
            )

    else:
        return Response(
            {
                "message": "diffrent user"
            },
            status = status.HTTP_400_BAD_REQUEST
        )


# 리뷰 좋아요/싫어요
@api_view(['POST',])
@permission_classes([IsAuthenticated,])
def review_likes(request, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    User = get_user_model()
    print(request.user.pk)
    user = User.objects.get(username=request.user)
    if review.user == request.user:
        return Response({ 'message': 'you can`t press likes your review'}, status=status.HTTP_400_BAD_REQUEST)
    if Review_likes.objects.filter(review=review, user=user):
        likes = get_object_or_404(Review_likes, review=review, user=user)
        print(likes)
        likes.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        # return Response({'message': 'You already like this review'}, status=status.HTTP_409_CONFLICT)
    serializer = ReviewLikesSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save(review=review, user=user)
        return Response(serializer.data, status.HTTP_201_CREATED)



# 후에 주석 처리할 내용들
# 초기 데이터 가져온 함수
@api_view(['GET', 'POST'])
def add_data(request):
    # url = "https://api.themoviedb.org/3/movie/now_playing?language=ko-US&page=1&region=KR"
    url = "https://api.themoviedb.org/3/movie/now_playing"
    for page in range(1, 11):
        params = {
            'language':'ko-US',
            'page':page,
            'region':'KR',
        }
        header = {'Authorization': 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI5NjhjZTg3MzRmNGEyMTU5NzdiNjkwODljYzg3M2JjYSIsInN1YiI6IjY1M2IxZWE4NzE5YWViMDEzODdiOWRkYSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.13M9hB1WM65LBn_iCieFJ9GWRzRn0dEA61JPrNBKazg',
                'accept': 'application/json',
                'append_to_response': 'images'
                }

        # 전송된 JSON 데이터를 받아옵니다.
        data = requests.get(url, headers=header, params=params).json()
        print(f'page: {page}')
        result_data = data['results']
        length = len(result_data)
        data_lst=[]

        for obj in result_data:
            # print(obj)
            if Movie.objects.filter(id=obj['id']).exists():
                continue
            data_lst.append({
                'adult': obj['adult'],
                'title': obj['title'],
                'id': obj['id'], 
                'original_title': obj['original_title'],
                'overview': obj['overview'],
                'popularity': obj['popularity'],
                'poster': obj['poster_path'],
                'release_date': obj['release_date'],
                'vote_average': obj['vote_average'],
                'vote_count': obj['vote_count'],
                'genres': obj['genre_ids']
            })
            # print(data_lst[i])
        print('i:', page ,'len:', len(result_data))
        # sleep(1)
        # Serializer를 사용하여 데이터를 파싱합니다.
        serializer = MovieSerializer(data=data_lst, many=True)
        if serializer.is_valid():
            # 데이터가 유효하면 저장합니다.
            serializer.save()
        else:
            break
    else:
        return Response({"message": "데이터가 성공적으로 추가되었습니다."})
    print('???')
    # 유효하지 않은 경우 에러 메시지를 반환합니다.
    return Response({"error": serializer.errors}, status=400)
    


@api_view(['GET'])
def add_genres(request):
    url = "https://api.themoviedb.org/3/genre/movie/list?language=ko"
    headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI5NjhjZTg3MzRmNGEyMTU5NzdiNjkwODljYzg3M2JjYSIsInN1YiI6IjY1M2IxZWE4NzE5YWViMDEzODdiOWRkYSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.13M9hB1WM65LBn_iCieFJ9GWRzRn0dEA61JPrNBKazg"
    }
    data = requests.get(url, headers=headers).json()['genres']
    print(data)
    # Serializer를 사용하여 데이터를 파싱합니다.
    serializer = GenreSerializer(data=data, many=True)

    if serializer.is_valid():
        # 데이터가 유효하면 저장합니다.
        serializer.save()
        return Response({"message": "데이터가 성공적으로 추가되었습니다."})
    else:
        print('???')
        # 유효하지 않은 경우 에러 메시지를 반환합니다.
        return Response({"error": serializer.errors}, status=400)
    
@api_view(['GET'])
@permission_classes([AllowAny])
def theater_detail(request, theater_pk):
    theater = Theater.objects.get(pk=theater_pk)
    serializer = TheaterSerializer(theater)
    
    return Response(serializer.data, status=status.HTTP_200_OK)