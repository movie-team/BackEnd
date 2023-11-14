from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings

# Create your models here.
class Genre(models.Model):
    id = models.IntegerField(primary_key = True)
    name = models.CharField(max_length=50)
    
class Movie(models.Model):
    id = models.IntegerField(primary_key=True)
    adult = models.BooleanField(default=True)
    title = models.CharField(blank=True, max_length=200)
    original_title = models.CharField(max_length=200)
    overview = models.TextField(blank=True)
<<<<<<< HEAD
    popularity = models.FloatField(blank=True)
    poster = models.TextField(blank=True, null=True)
    release_date = models.DateField()
    vote_average = models.FloatField()
    vote_count = models.IntegerField()
=======
    poster = models.ImageField(blank=True)
    id = models.IntegerField(primary_key=True)
    adult = models.BooleanField()
>>>>>>> 9e83e5bedf4656dd83638095323942b6ac48336a
    created_at = models.DateField(auto_now_add=True)
    genres = models.ManyToManyField(Genre, verbose_name='test_movie', unique=False)


class Review(models.Model):
    movie_pk = models.ForeignKey(Movie, on_delete=models.CASCADE)
    content = models.TextField()
    rating = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    user_pk = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

class Review_likes(models.Model):
    user_pk = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    review_pk = models.ForeignKey(Review, on_delete=models.CASCADE)
    review_likes = models.BooleanField()

class Test_model(models.Model):
    id = models.IntegerField(primary_key=True)
    adult = models.BooleanField(blank=True, default=True)
    title = models.CharField(max_length=200)
    original_title = models.CharField(blank=True, default= None, max_length=200)
    overview = models.TextField(blank=True)
    popularity = models.FloatField(blank=True)
    poster = models.TextField(blank=True, null=True)
    release_date = models.DateField(blank=True)
    vote_average = models.FloatField(blank=True)
    vote_count = models.IntegerField(blank=True)
    genres = models.ManyToManyField(Genre, verbose_name='test_movie', unique=False)
    
