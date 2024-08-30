from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    RegexValidator, MaxValueValidator, MinValueValidator
)
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Avg
from django.utils import timezone


# Импортируем константы
from api.constants import (USERNAME_MAX_LENGTH, EMAIL_MAX_LENGTH,
                           BIO_MAX_LENGTH, CONFIRMATION_CODE_MAX_LENGTH,
                           CATEGORY_NAME, CATEGORY_SLUG, GENRE_NAME,
                           GENRE_SLUG, TITLE_NAME, SCORE_MAX_VALUE_VALIDATOR,
                           SCORE_MIN_VALUE_VALIDATOR, TEXT_SYMBOL_SLICE)


class CustomUser(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        MODER = 'moderator', 'Moderator'
        USER = 'user', 'User'

    username_validator = RegexValidator(
        regex=r'^[\w.@+-]+\Z',
        message='Неверный формат Username',
    )
    username = models.CharField('Юзернейм', max_length=USERNAME_MAX_LENGTH,
                                unique=True,
                                blank=False)
    email = models.EmailField('Почта', max_length=EMAIL_MAX_LENGTH,
                              unique=True,
                              blank=False)
    first_name = models.CharField('Имя', max_length=USERNAME_MAX_LENGTH,
                                  blank=True,)
    last_name = models.CharField('Фамилия', max_length=USERNAME_MAX_LENGTH,
                                 blank=True,)
    bio = models.TextField('Биография', max_length=BIO_MAX_LENGTH, blank=True)
    role = models.CharField(
        'Роль', max_length=max(len(role) for role, _ in Roles.choices),
        choices=Roles.choices,
        default='user')
    confirmation_code = models.CharField(
        'Код',
        max_length=CONFIRMATION_CODE_MAX_LENGTH,
        blank=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ('email', )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_moderator(self):
        return self.role == CustomUser.Roles.MODER

    @property
    def is_admin(self):
        return (self.role == CustomUser.Roles.ADMIN or self.is_superuser
                or self.is_staff)

    def clean(self):
        super().clean()
        if self.username == 'me':
            raise ValidationError('Такое имя запрещено')

    def __str__(self):
        return self.username


class Category(models.Model):
    name = models.CharField(max_length=CATEGORY_NAME, verbose_name='Категория')
    slug = models.SlugField(max_length=CATEGORY_SLUG, unique=True,
                            verbose_name='Слаг')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(models.Model):
    name = models.CharField(max_length=GENRE_NAME, verbose_name='Жанр')
    slug = models.SlugField(max_length=GENRE_SLUG, unique=True,
                            verbose_name='Слаг')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


def validate_year(value):
    current_year = timezone.now().year
    if value > current_year:
        raise ValidationError(
            f'Год не может быть больше текущего {current_year}'
        )


def validate_year(value):
    current_year = timezone.now().year
    if value > current_year:
        raise ValidationError(f'Год не может быть больше текущего {current_year}')


class Title(models.Model):
    name = models.CharField(max_length=TITLE_NAME, verbose_name='Название')
    year = models.SmallIntegerField(
        verbose_name='Год',
        db_index=True,
        validators=[validate_year]
    )
    description = models.TextField(verbose_name='Описание')
    genre = models.ManyToManyField(Genre, verbose_name='Жанр')
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name='titles',
        verbose_name='Категория')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'


class Review(models.Model):
    text = models.TextField(verbose_name='Текст')
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews',
        verbose_name='Произведение')
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='reviews',
        verbose_name='Автор')
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(SCORE_MIN_VALUE_VALIDATOR),
                    MaxValueValidator(SCORE_MAX_VALUE_VALIDATOR)],
        verbose_name='Оценка')
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
        CustomUser, on_delete=models.CASCADE, related_name='comments',
        verbose_name='Автор')
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments',
        verbose_name='Отзыв')
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:TEXT_SYMBOL_SLICE]
