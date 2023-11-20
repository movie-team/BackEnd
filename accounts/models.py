from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from datetime import datetime

class UserManager(BaseUserManager):
    def create_user(self, username, password, birth, **extra_fields):
        if not username:
            raise ValueError('Users must have an username address')
        
        
        current_date = datetime.now()

        date_format = "%Y-%m-%d"
        user_birth = datetime.strptime(birth, date_format)

        date_diff = current_date - user_birth

        user_age = date_diff.days / 365.25

        user = self.model(
            username=username,
            birth=birth,
            age=user_age,
            **extra_fields
        )
        user.set_password(password)
        user.save(using = self._db)
        return user
    
    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('email', 'sirlyun23@gmail.com')
        extra_fields.setdefault('birth', '1999-12-24'),
        extra_fields.setdefault('gender', True)

        return self.create_user(username, password, **extra_fields)

    

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=20, unique=True, null=False, blank=False)
    email = models.EmailField(max_length=30, blank=False)
    first_name = models.CharField(max_length=20, default=False, blank=True)
    last_name = models.CharField(max_length=20, default=False, blank=True)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    social = models.BooleanField(default=False, blank=True)
    gender = models.BooleanField(blank=False)
    birth = models.CharField(max_length=40, blank=False)
    age = models.IntegerField(blank=True)

	# 헬퍼 클래스 사용
    objects = UserManager()

    USERNAME_FIELD = 'username'