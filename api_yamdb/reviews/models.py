from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.core.validators import (RegexValidator, MaxLengthValidator,
                                    MinLengthValidator)
from django.db import models


class CustomUser(AbstractUser):
    ROLES = [  # Роли указаны в верхнем и нижнем регистре
        ('user', 'User'),
        ('moderator', 'Moderator'),
        ('admin', 'Admin'),
    ]
    username_validator = RegexValidator(
        regex=r'^[\w.@+-]+\Z',
        message="Неверный формат Username",
    )
    username = models.CharField(max_length=150, unique=True, blank=False)
    email = models.EmailField(max_length=254, unique=True, blank=False)
    first_name = models.CharField(max_length=150, blank=True,)
    last_name = models.CharField(max_length=150, blank=True,)
    bio = models.TextField(max_length=250, blank=True)
    role = models.CharField(max_length=10, choices=ROLES, default='user')
    confirmation_code = models.CharField(max_length=500, blank=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ('email', )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Genre(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=256)
    year = models.IntegerField()
    description = models.TextField()
    genre = models.ManyToManyField(Genre)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name


class Review(models.Model):
    text = models.TextField()
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews')
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='reviews')
    score = models.IntegerField()
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)


class Comment(models.Model):
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='comments')
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)