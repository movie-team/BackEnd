from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404, get_list_or_404
from django.contrib.auth import get_user_model
from .serializers import MovieSerializer, TestSerializer, GenreSerializer, ReviewSerializer
from .models import Movie, Genre, Test_model, Review

from rest_framework import status

import requests
import json
from rest_framework.permissions import AllowAny, IsAuthenticated

from pprint import pprint
from time import sleep

# Create your views here.

@api_view(['GET',])
@permission_classes([AllowAny,])
def movie_list(request):
    if request.method == 'GET':
        movies = get_list_or_404(Movie)
        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data)


@api_view(['GET',])
@permission_classes([AllowAny,])
def movie_detail(request, movie_pk):
    movie = get_object_or_404(Movie, id=movie_pk)
    if request.method == 'GET':
        serializer = MovieSerializer(movie)
        print(serializer.data)
        return Response(serializer.data)
    
@api_view(['GET'])
@permission_classes([AllowAny,])
def review(request, movie_pk):
    movie = get_object_or_404(Movie, id=movie_pk)
    reviews = movie.review_set.all()
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)



@api_view(['POST'])
@permission_classes([IsAuthenticated, ])
def review_create(request, movie_pk):
    movie = get_object_or_404(Movie, id=movie_pk)
    user = request.user
    serializer = ReviewSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(movie=movie, user=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated, ])
def review_control(request, movie_pk, review_pk):
    user = request.user
    review = Review.objects.get(pk=review_pk)

    check_user = review.user_id

    if user.id == check_user:
        if request.method == 'PUT':
            serializer = ReviewSerializer(review, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)

        elif request.method == 'DELETE':
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