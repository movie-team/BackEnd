from rest_framework import serializers
from .models import Movie, Test_model, Genre, Review

class MovieSerializer(serializers.ModelSerializer):
    genres = serializers.PrimaryKeyRelatedField(many=True, queryset=Genre.objects.all())
    
    def create(self, validated_data): # 이거 추가됨
        # return super().create(validated_data)
        genres_ids = validated_data.pop('genres')
        test = Movie.objects.create(**validated_data)
        test.genres.set(genres_ids)
        return test
    
    class Meta:
        model = Movie
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ('movie', 'user')




class GenreSerializer(serializers.ModelSerializer):
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