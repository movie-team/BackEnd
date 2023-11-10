from rest_framework import serializers
from .models import Movie, Test_model, Genre

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        # fields = '__all__'
        fields = ['id']


class TestSerializer(serializers.ModelSerializer):
    # genres = GenreSerializer(read_only=True, many=True)
    genres = GenreSerializer(many=True)
    class Meta:
        model = Test_model
        fields = '__all__'