from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404, get_list_or_404
from django.contrib.auth import get_user_model
from .serializers import MovieSerializer, TestSerializer, GenreSerializer, ReviewSerializer, ReviewLikesSerializer, TheaterSerializer, SeatSerializer, TicketSerializer, PaymentSerializer
from .models import Movie, Genre, Test_model, Review, Review_likes, Theater, Seat, Ticket, Payment
from rest_framework import status

import requests
import json
from rest_framework.permissions import AllowAny, IsAuthenticated

from django.db.models import Avg, Count
import numpy as np
from django.db import transaction
from PJT.settings import SOCIAL_OUTH_CONFIG, BASE_URL
import random

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
    movies = get_list_or_404(Movie.objects.order_by('-popularity'))[:10]
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

# 유저가 속한 연령대, 성별의 평점을 반환하는 함수
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

# 연령대, 성별에 따른 평점을 반환하는 함수
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
            group = reviews.aggregate(Avg("rating"),Count("rating"))
            print(group)
            group['gender'] = gender
            group['age_group'] = age_group
            rating_list.append(group)
    return Response(rating_list)

# 유저 협업필터링 추천 알고리즘
@api_view(['GET'])
@permission_classes([IsAuthenticated,])
def user_recommend(request):
    movies = Movie.objects.all()
    User = get_user_model()
    users = User.objects.all()

    # 벡터 설정
    vectors = {}
    for user in users:
        vectors[user.pk] = {movie.id: 0 for movie in movies}
        for info in user.reviews.values('movie', 'rating'):
            vectors[user.pk][info['movie']] = info['rating']
    # print(vectors)

    # 코사인 유사도 계산
    user_vector = list(vectors[request.user.pk].values())
    user_movies = [review['movie_id'] for review in request.user.reviews.values('movie_id')]
    for key, vector in vectors.items():
        if key == request.user.pk:
            vectors[key] = -1
            continue
        vector = list(vector.values())
        if np.linalg.norm(vector) == 0:
            vectors[key] = 0
            continue
        similarity = np.dot(user_vector,vector)/(np.linalg.norm(user_vector)*np.linalg.norm(vector))        
        vectors[key] = similarity
    # print(vectors)
    sorted_vector = sorted(vectors.items(), key=lambda item: item[1], reverse=True)
    # print(user_movies)


    # 추천 리스트 생성
    recommend_list = []
    target_num_of_movies = 5 # 추천할 영화 개수
    # print(sorted_vector)
    for su_pk, similarity in sorted_vector:
        su = User(pk=su_pk)
        su_avg = su.reviews.all().aggregate(Avg('rating'))['rating__avg']
        # print('??', su_avg)
        if su_avg == None:
            su_avg = 0
        su_movies = su.reviews.filter(rating__gte=su_avg).exclude(movie__id__in=user_movies).order_by('-rating').values('movie_id')
        for su_movie in su_movies:
            movie = get_object_or_404(Movie, id=su_movie['movie_id'])
            if movie not in recommend_list:
                recommend_list.append(movie)
                target_num_of_movies -= 1
                if target_num_of_movies <= 0:
                    break
        else:
            continue
        break
    # print(recommend_list)

    # serialize
    serializer = MovieSerializer(recommend_list, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny,])
def review(request, movie_pk):
    movie = get_object_or_404(Movie, id=movie_pk)
    reviews = movie.reviews.all()
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
    user = User.objects.get(username=request.user)

    # 리뷰 작성자와 요청자가 같은 경우
    if review.user == request.user:
        return Response({ 'message': 'you can`t press likes your review'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 이미 좋아요/싫어요를 누른 경우
    if Review_likes.objects.filter(review=review, user=user):
        likes = get_object_or_404(Review_likes, review=review, user=user)
        # print(request.data['review_likes'] == str(likes.review_likes))

        # 취소하는 경우
        if request.data['review_likes'] == likes.review_likes:
            likes.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        # 바꾸는 경우
        else:
            serializer = ReviewLikesSerializer(likes, data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
    
    serializer = ReviewLikesSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save(review=review, user=user)
        return Response(serializer.data, status.HTTP_201_CREATED)


# 월드컵
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated,])
def worldcup(request):
    if request.method == 'GET':
        # 추천할 만한 영화를 추출 (16개)
        unreviewed_movies = Movie.objects.exclude(reviews__user=request.user).order_by('?')[:16]
        # print('?', len(unreviewed_movies), unreviewed_movies)
        serializer = MovieSerializer(unreviewed_movies, many=True)
        return Response(serializer.data)
    
    # 월드컵 결과를 기반으로 장르의 코사인 유사도를 통한 추천 알고리즘
    elif request.method == 'POST':
        genres = Genre.objects.values('id')
        vector = { genre['id']: { 'wins': 0, 'matches': 0 } for genre in genres}
        # 총 승리수 / 총 매치수로 벡터를 설정
        for k, v in request.data['val'].items():
            movie = get_object_or_404(Movie, id=k)
            movie_genres = [genre['id'] for genre in movie.genres.values('id')]
            v = int(v)
            for genre in movie_genres:
                vector[genre]['wins'] = v
                if v >= 4:
                    vector[genre]['matches'] = v
                    winner_movie = movie
                else:
                    vector[genre]['matches'] = v + 1
        for k, v in vector.items():
            if v['matches'] == 0:
                vector[k] = 0
                continue
            vector[k] = v['wins']/v['matches']
        vector = list(vector.values())

        # 모든 영화의 코사인 유사도 계산
        movies_similarity = {}
        movies = Movie.objects.all()
        for movie in movies:
            movies_similarity[movie.id] = 0
            movie_genres = [genre['id'] for genre in movie.genres.values('id')]
            movie_vector = { genre['id']: 0 for genre in genres}
            for movie_genre in movie_genres:
                movie_vector[movie_genre] = 1
            movie_vector = list(movie_vector.values())
            similarity = np.dot(vector,movie_vector)/(np.linalg.norm(vector)*np.linalg.norm(movie_vector))
            movies_similarity[movie.id] = similarity
        
        # 유사도 내림차순으로 정렬
        sorted_similarity = sorted(movies_similarity.items(), key= lambda item: item[1], reverse=True)
        movies_list = []

        # 월드컵에 나오지 않은 영화 중 가장 코사인 유사도가 높은 영화 5개를 추출
        count = 0
        while len(movies_list) < 5:
            id = sorted_similarity[count][0]
            if str(id) in request.data.keys():
                count += 1
                continue
            movies_list.append(get_object_or_404(Movie, id=id))
            count += 1
        winner_serializer = MovieSerializer(winner_movie)
        serializer = MovieSerializer(movies_list, many=True)
        return Response({ 'recommend': serializer.data,
                         'winner': winner_serializer.data})

# 상영관 상세
@api_view(['GET'])
@permission_classes([AllowAny])
def theater_detail(request, theater_pk):
    theater = Theater.objects.get(pk=theater_pk)
    serializer = TheaterSerializer(theater)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


# 티켓 생성
# req body에 좌석 번호 필요
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def ticket_create(request):
    if request.method == 'GET':
        tickets = Ticket.objects.filter(user=request.user, check=False)
        serializer = TicketSerializer(tickets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'POST':

        user = request.user
        seats = request.data.get('seat', [])

        with transaction.atomic():
            tickets = []
            for seat in seats:
                seat_instance = Seat.objects.get(pk=seat)
                if seat_instance.check:
                    return Response({'message': 'already reserved'}, status=status.HTTP_400_BAD_REQUEST)
                data = {'seat': seat_instance, 'user': user}
                serializer = TicketSerializer(data=data)
                if serializer.is_valid():
                    ticket = serializer.save(seat=seat_instance, user=user)
                    ticket_serializer = TicketSerializer(ticket)
                    tickets.append(ticket_serializer.data)
                else:
                    return Response({'message': 'Invalid request. Check your data.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'tickets': tickets, 'message': 'Tickets created successfully'}, status=status.HTTP_201_CREATED)

# 티켓 좌석별 삭제
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def ticket_delete(request, seat_pk):
    user = request.user
    ticket = Ticket.objects.get(seat_id=seat_pk)
    check_user = ticket.user_id

    if user.id == check_user:
        if request.method == 'DELETE':

            ticket.delete()
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
    
# 티켓 전체 삭제
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_all(request):
    user = request.user
    

    if request.method == 'DELETE':
        for ticket in Ticket.objects.filter(user=user):
            if not ticket.check:
                ticket.delete()
        return Response(
            {
                "message": "delete success"
            },
            status = status.HTTP_204_NO_CONTENT
            )


# 결제 요청
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ticket_pay(request):
    tickets = Ticket.objects.filter(user=request.user, check=False)
    seat_set = []
    cnt = 0
    for ticket in tickets:
        cnt += 1
        seat_set.append(ticket.seat.id)

    if cnt > 0:
        data = {
                'cid': 'TC0ONETIME',
                'partner_order_id': request.user.id,
                'partner_user_id': request.user.username,
                'item_name': 'ticket',
                'quantity': cnt,
                'total_amount': 10000*cnt,
                'tax_free_amount': 0,
                'approval_url': f'{BASE_URL}/api/movies/success/',
                'fail_url': f'{BASE_URL}/api/movies/fail/',
                'cancel_url': f'{BASE_URL}/api/movies/cancel/'
            }
        headers = {
            'Authorization': f'KakaoAK {SOCIAL_OUTH_CONFIG["SERVICE_APP_ADMIN_KEY"]}',
            'Content-type': 'application/x-www-form-urlencoded;charset=utf-8'
        }
        url = 'https://kapi.kakao.com/v1/payment/ready'
        response = requests.post(url, data=data, headers=headers)
        res = response.json()

        for s in seat_set:
            seat = Seat.objects.get(id=s)
        
            req = {
                'tid': res['tid']
            }
            serializer = PaymentSerializer(data=req)
            if Payment.objects.filter(ticket=Ticket.objects.get(seat=seat)).exists():
                return Response({
                    'message': "already did"
                }, status=status.HTTP_400_BAD_REQUEST)
            if serializer.is_valid():
                serializer.save(ticket=Ticket.objects.get(seat=seat))

        return Response(res, status=status.HTTP_200_OK)
    else:
        return Response({
            'message': 'nothing to pay'
        }, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
@permission_classes([AllowAny])
def success(request):
    pg_token = request.GET.get('pg_token')
    return redirect(f'{SOCIAL_OUTH_CONFIG["LOGOUT_REDIRECT_URI"]}tickets/pay?pg_token={pg_token}')

# 결제 승인
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def payConfirm(request):
    ticket = Ticket.objects.filter(user=request.user, check=False)
    payment = Payment.objects.get(ticket=ticket[0])
    data = {
            'cid': 'TC0ONETIME',
            'tid': payment.tid,
            'partner_order_id': request.user.id,
            'partner_user_id': request.user.username,
            'pg_token': request.data['pg_token']
        }
    url = "https://kapi.kakao.com/v1/payment/approve"

    headers = {
        'Authorization': f'KakaoAK {SOCIAL_OUTH_CONFIG["SERVICE_APP_ADMIN_KEY"]}',
        'Content-type': 'application/x-www-form-urlencoded;charset=utf-8'
    }
    response = requests.post(url, data=data, headers=headers)

    
    for tmp in Ticket.objects.filter(user=request.user):
        for pay in tmp.payment_set.all():
            pay.check = True
            pay.save()
        seat = tmp.seat
        seat.check = True
        seat.save()
        seat.theater.rest_seat -= 1
        seat.theater.save()
        tmp.check = True
        tmp.save()

    return Response(response.json())


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def payCancel(request):
    payment_pk = request.data['payment']
    response = []
    for pk in payment_pk:
        payment = Payment.objects.get(pk=pk)
        ticket = Ticket.objects.get(pk=payment.ticket_id)
        if request.user == ticket.user:
            url = 'https://kapi.kakao.com/v1/payment/cancel'
            headers = {
                'Authorization': f'KakaoAK {SOCIAL_OUTH_CONFIG["SERVICE_APP_ADMIN_KEY"]}',
                'Content-type': 'application/x-www-form-urlencoded;charset=utf-8'
            }
            data = {
                'cid': 'TC0ONETIME',
                'tid': payment.tid,
                'cancel_amount': 10000,
                'cancel_tax_free_amount': 0
            }
            res = requests.post(url, headers=headers, data=data)
            response.append(res.json())
            ticket.seat.check = False
            ticket.seat.save()
            ticket.seat.theater.rest_seat += 1
            ticket.seat.theater.save()
            ticket.delete()
            

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    return Response(response, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment(request):
    ticekts = Ticket.objects.filter(user=request.user, check=True)
    response = {}
    for ticket in ticekts:
        payment = ticket.payment_set.all()
        response[f'{ticket.id}'] = payment[0].id
    return Response(response, status=status.HTTP_200_OK)

