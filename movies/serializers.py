from rest_framework import serializers
from .models import Movie, Test_model, Genre, Review, Review_likes, Theater, Seat, Ticket
from accounts.serializers import UserSerializer

class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = '__all__'
        read_only_fields = ('theater',)

class TheaterSerializer(serializers.ModelSerializer):
    seat_set = SeatSerializer(many=True, read_only=True)
    class Meta:
        model = Theater
        fields = '__all__'
        read_only_fields = ('movie',)

class MovieSerializer(serializers.ModelSerializer):
    genres = serializers.PrimaryKeyRelatedField(many=True, queryset=Genre.objects.all())
    theater_set = TheaterSerializer(many=True, read_only=True)
    def create(self, validated_data): # 이거 추가됨
        # return super().create(validated_data)
        genres_ids = validated_data.pop('genres')
        test = Movie.objects.create(**validated_data)
        test.genres.set(genres_ids)
        return test
    
    class Meta:
        model = Movie
        fields = '__all__'


class TicketSerializer(serializers.ModelSerializer):
    # seat = SeatSerializer()
    class Meta:
        model = Ticket
        fields = '__all__'
        read_only_fields = ('seat', 'user',)


class ReviewLikesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review_likes
        fields = '__all__'
        read_only_fields = ('user', 'review')

class ReviewSerializer(serializers.ModelSerializer):
    likes = ReviewLikesSerializer(many=True, read_only=True)
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    user = UserSerializer(read_only=True)
    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ('movie', 'user')



class GenreSerializer(serializers.ModelSerializer):
    movies = MovieSerializer(many=True, read_only=True)


    class Meta:
        model = Genre
        fields = '__all__'


class TestSerializer(serializers.ModelSerializer):
    # genres = GenreSerializer(read_only=True, many=True)
    genres = serializers.PrimaryKeyRelatedField(many=True, queryset=Genre.objects.all())
    
    def create(self, validated_data): # 이거 추가됨
        # return super().create(validated_data)
        genres_ids = validated_data.pop('genres')
        test = Test_model.objects.create(**validated_data)
        test.genres.set(genres_ids)
        return test
    
    class Meta:
        model = Test_model
        fields = '__all__'



