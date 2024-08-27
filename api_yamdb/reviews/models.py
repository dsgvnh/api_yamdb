from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    RegexValidator, MaxValueValidator, MinValueValidator
)
from django.db import models
from django.db.models import Avg

# Импортируем константы
from api.constants import USERNAME_MAX_LENGTH, EMAIL_MAX_LENGTH, ROLE_MAX_LENGTH, BIO_MAX_LENGTH, ROLES, USER_ROLE, CONFIRMATION_CODE_MAX_LENGTH, YEAR_MAX_LENGTH

class CustomUser(AbstractUser):
    username_validator = RegexValidator(
        regex=r'^[\w.@+-]+\Z',
        message="Неверный формат Username",
    )
    username = models.CharField(
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        blank=False,
        verbose_name='Имя пользователя'
    )
    email = models.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
        blank=False,
        verbose_name='Email'
    )
    first_name = models.CharField(max_length=USERNAME_MAX_LENGTH, blank=True, verbose_name='Имя')
    last_name = models.CharField(max_length=USERNAME_MAX_LENGTH, blank=True, verbose_name='Фамилия')
    bio = models.TextField(max_length=BIO_MAX_LENGTH, blank=True, verbose_name='Биография')
    role = models.CharField(
        max_length=ROLE_MAX_LENGTH,
        choices=ROLES,
        default=USER_ROLE,
        verbose_name='Роль'
    )
    confirmation_code = models.CharField(max_length=CONFIRMATION_CODE_MAX_LENGTH, blank=True, verbose_name='Код подтверждения')

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ('email', )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_moderator(self):
        return self.role == MODERATOR_ROLE

    @property
    def is_admin(self):
        return self.role == ADMIN_ROLE or self.is_superuser or self.is_staff

    def __str__(self):
        return self.username


class Category(models.Model):
    name = models.CharField(max_length=256, verbose_name='Категория')
    slug = models.SlugField(max_length=50, unique=True, verbose_name='Слаг')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(models.Model):
    name = models.CharField(max_length=256, verbose_name='Жанр')
    slug = models.SlugField(max_length=50, unique=True, verbose_name='Слаг')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    name = models.CharField(max_length=256, verbose_name='Название')
    year = models.SmallIntegerField(verbose_name='Год', db_index=True)
    description = models.TextField(verbose_name='Описание')
    genre = models.ManyToManyField(Genre, verbose_name='Жанр')
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name='titles', verbose_name='Категория')

    @property
    def rating(self):
        return self.reviews.aggregate(avg_score=Avg('score'))['avg_score']

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'


class Review(models.Model):
    text = models.TextField(verbose_name='Текст')
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews', verbose_name='Произведение')
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='reviews', verbose_name='Автор')
    score = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)], verbose_name='Оценка')
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_author_title'
            )
        ]
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'


class Comment(models.Model):
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='comments', verbose_name='Автор')
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments', verbose_name='Отзыв')
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:20]
