# Standard library imports
from django.core.validators import (
    RegexValidator, MaxLengthValidator, MinLengthValidator
)

# Third-party imports
from rest_framework import serializers
from datetime import datetime

# Local application imports
from reviews.models import (
    Category, Genre, Title, CustomUser, Review, Comment
)

from .constants import (USERNAME_MAX_LENGTH, EMAIL_MAX_LENGTH,
                        MIN_USERNAME_LENGTH, BIO_MAX_LENGTH,
                        FORBIDDEN_USERNAMES)


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=USERNAME_MAX_LENGTH,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message=(
                    'Username должен содержать только буквы, '
                    'цифры и символы: @ . + -'
                ),
                code='invalid_username'
            )
        ],
        required=True,
    )
    confirmation_code = serializers.CharField(required=True)

    def validate_username(self, value):
        if value.lower() in FORBIDDEN_USERNAMES:
            raise serializers.ValidationError("Этот username запрещен.")
        return value


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=USERNAME_MAX_LENGTH,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message=(
                    'Username должен содержать только буквы, '
                    'цифры и символы: @ . + -'
                ),
                code='invalid_username'
            )
        ], required=True
    )
    email = serializers.EmailField(
        max_length=EMAIL_MAX_LENGTH, required=True
    )
    first_name = serializers.CharField(
        max_length=USERNAME_MAX_LENGTH, required=False
    )
    last_name = serializers.CharField(
        max_length=USERNAME_MAX_LENGTH, required=False
    )
    bio = serializers.CharField(
        max_length=BIO_MAX_LENGTH, required=False
    )
    role = serializers.ChoiceField(CustomUser.Roles.choices, required=False)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')

    def validate(self, data):
        email = data.get('email')
        username = data.get('username')
        if username in FORBIDDEN_USERNAMES:
            raise serializers.ValidationError(
                {'username': 'Запрещенное имя'})
        known_username = CustomUser.objects.filter(username=username).first()
        known_email = CustomUser.objects.filter(email=email).first()
        if known_username:
            if (known_username.email != email):
                raise serializers.ValidationError(
                    {'mail': 'Несуществующая почта'})
        if known_email:
            if (known_email.username != username):
                raise serializers.ValidationError(
                    {'username': 'Несуществующее имя'})
        return data


class RegisterSerializer(serializers.Serializer):
    username_validator = RegexValidator(
        regex=r'^[\w.@+-]+\Z',
        message="Неверный формат Username",
    )
    username = serializers.CharField(
        validators=[username_validator,
                    MinLengthValidator(MIN_USERNAME_LENGTH),
                    MaxLengthValidator(USERNAME_MAX_LENGTH)],
        required=True,
    )
    email = serializers.EmailField(max_length=EMAIL_MAX_LENGTH, required=True)

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        if CustomUser.objects.filter(email=email, username=username).exists():
            return data
        if (CustomUser.objects.filter(email=email).exists()
                and CustomUser.objects.filter(username=username).exists()):
            raise serializers.ValidationError({
                'email': 'Такая почта уже занята',
                'username': 'Такое имя уже занято'
            })
        if CustomUser.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {'email': 'Такая почта уже занята'})
        if (CustomUser.objects.filter(username=username).exists()
                or username == 'me'):
            raise serializers.ValidationError(
                {'username': 'Такое имя уже занято'})
        return data

    def create(self, validated_data):
        email = validated_data.get('email')
        username = validated_data.get('username')
        user, created = CustomUser.objects.get_or_create(email=email,
                                                         username=username)
        return user


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitlePostSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all(), required=True)
    genre = serializers.SlugRelatedField(
        slug_field='slug', queryset=Genre.objects.all(), many=True,
        required=True)

    class Meta:
        model = Title
        fields = '__all__'

    def validate_year(self, value):
        if value > datetime.now().year:
            raise serializers.ValidationError('Year cannot be in the future.')
        return value

    def validate_genre(self, value):
        if not value:
            raise serializers.ValidationError('Genre field cannot be empty.')
        return value

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['category'] = CategorySerializer(instance.category).data
        ret['genre'] = GenreSerializer(instance.genre.all(), many=True).data
        ret['rating'] = instance.rating
        return ret


class TitleGetSerializer(serializers.ModelSerializer):
    rating = serializers.FloatField(read_only=True)
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Title
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        if not self.context.get('request').method == 'POST':
            return data
        author = self.context.get('request').user
        title_id = self.context.get('view').kwargs.get('title_id')
        if Review.objects.filter(author=author, title=title_id).exists():
            raise serializers.ValidationError(
                'Нельзя оставить два отзыва'
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
