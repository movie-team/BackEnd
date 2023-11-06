from django.db import models

# Create your models here.
class Movies(models.Model):
    title = models.CharField(max_length=50)
    overview = models.TextField(blank=True)
    poster = models.ImageField(blank=True)
    created_at = models.DateField(auto_now_add=True)