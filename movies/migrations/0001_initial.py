# Generated by Django 3.2 on 2023-11-15 06:41

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('adult', models.BooleanField(default=True)),
                ('title', models.CharField(blank=True, max_length=200)),
                ('original_title', models.CharField(max_length=200)),
                ('overview', models.TextField(blank=True)),
                ('popularity', models.FloatField(blank=True)),
                ('poster', models.TextField(blank=True, null=True)),
                ('release_date', models.DateField()),
                ('vote_average', models.FloatField()),
                ('vote_count', models.IntegerField()),
                ('created_at', models.DateField(auto_now_add=True)),
                ('genres', models.ManyToManyField(to='movies.Genre', verbose_name='test_movie')),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('rating', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(5.0)])),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='movies.movie')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Test_model',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('adult', models.BooleanField(blank=True, default=True)),
                ('title', models.CharField(max_length=200)),
                ('original_title', models.CharField(blank=True, default=None, max_length=200)),
                ('overview', models.TextField(blank=True)),
                ('popularity', models.FloatField(blank=True)),
                ('poster', models.TextField(blank=True, null=True)),
                ('release_date', models.DateField(blank=True)),
                ('vote_average', models.FloatField(blank=True)),
                ('vote_count', models.IntegerField(blank=True)),
                ('genres', models.ManyToManyField(to='movies.Genre', verbose_name='test_movie')),
            ],
        ),
        migrations.CreateModel(
            name='Review_likes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('review_likes', models.BooleanField()),
                ('review', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='movies.review')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
