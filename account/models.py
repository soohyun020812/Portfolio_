from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = models.CharField(
        max_length=20,
        blank=False,
        unique=True,
        verbose_name="닉네임",
        validators=[
            RegexValidator(
                regex="^[a-zA-Z0-9_]*$",
                message="이 필드에는 영문자, 숫자, 밑줄만 포함할 수 있습니다.",
            )
        ],
    )
    email = models.EmailField(max_length=50, unique=True, verbose_name="이메일")

    # 추가 요구사항: 프로필 사진을 위한 필드
    profile_picture = models.ImageField(
        upload_to="profile_pictures/", null=True, blank=True, verbose_name="프로필 사진"
    )

    # 추가 요구사항: 사용자의 나이를 저장하는 필드
    age = models.PositiveIntegerField(null=True, blank=True, verbose_name="나이")

    # 추가 요구사항: 사용자의 소개를 저장하는 필드
    # bio = models.TextField(max_length=300, blank=True, verbose_name='소개')

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = CustomUserManager()

    def __str__(self):
        return self.email
