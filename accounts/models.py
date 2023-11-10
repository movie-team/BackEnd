from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, password, **kwargs):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(
            email = email,
        )
        user.set_password(password)
        user.save(using = self._db)
        return user
    

class User(AbstractBaseUser):
    
    email = models.EmailField(max_length=30, unique=True, null=False, blank=False)
    first_name = models.CharField(max_length=20, default=False, blank=True)
    last_name = models.CharField(max_length=20, default=False, blank=True)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

	# 헬퍼 클래스 사용
    objects = UserManager()

	# 사용자의 username field는 email으로 설정 (이메일로 로그인)
    USERNAME_FIELD = 'email'