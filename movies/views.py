from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import MovieSerializer, TestSerializer, GenreSerializer
from .models import Movie, Genre
import requests
import json
from pprint import pprint

# Create your views here.
@api_view(['GET', 'POST'])
def add_data(request):
    url = "https://api.themoviedb.org/3/movie/now_playing?language=ko-US&page=1&region=KR"
    header = {'Authorization': 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI5NjhjZTg3MzRmNGEyMTU5NzdiNjkwODljYzg3M2JjYSIsInN1YiI6IjY1M2IxZWE4NzE5YWViMDEzODdiOWRkYSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.13M9hB1WM65LBn_iCieFJ9GWRzRn0dEA61JPrNBKazg',
            'accept': 'application/json',
            'append_to_response': 'images'
            }

    # 전송된 JSON 데이터를 받아옵니다.
    data = requests.get(url, headers=header).json()
    print(data['results'][0])
    result_data = data['results']
    length = len(result_data)
    data_lst=[{}]*length
    for i, obj in enumerate(result_data):
        # print(obj)
        data_lst[i] = {
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
            # 'genres': obj['genre_ids'], 
            # 'genres': [{'id': id, 'name': Genre.objects.get(id=id).name} for id in obj['genre_ids']]
            'genres': [{'id': id} for id in obj['genre_ids']]
            # 'genres': [Genre.objects.get(id=id) for id in obj['genre_ids']]
        }
        # print(data_lst[i])
    print('len:', len(result_data))
    # Serializer를 사용하여 데이터를 파싱합니다.
    serializer = TestSerializer(data=data_lst, many=True)

    if serializer.is_valid():

        # 데이터가 유효하면 저장합니다.
        # print(serializer)
        # pprint(serializer.data)
        # for 
        for i, d in enumerate(serializer.data):
            d['genres'] = result_data[i]['genre_ids']
            pprint(d['genres'])
            pprint(d)
        serializer.save()
        return Response({"message": "데이터가 성공적으로 추가되었습니다."})
    else:
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