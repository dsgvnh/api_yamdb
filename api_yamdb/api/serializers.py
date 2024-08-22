from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from reviews.models import Category, Genre, Title, CustomUser
from django.contrib.auth.tokens import default_token_generator
import re
from django.core.validators import (RegexValidator, MaxLengthValidator,
                                    MinLengthValidator)


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('username', 'confirmation_code', )


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',  # Паттерн для проверки username
                message='Username должен содержать только буквы, цифры и символы: @ . + -',
                code='invalid_username'
            )
        ]
    )
    email = serializers.EmailField(
        max_length=254,
        validators=[UniqueValidator(queryset=CustomUser.objects.all())]
    )
    first_name = serializers.CharField(
        max_length=150,
    )
    last_name = serializers.CharField(
        max_length=150,
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')

    def validate(self, data):
        email = data.get('email')
        username = data.get('username')
        known_username = CustomUser.objects.filter(username=username)
        known_email = CustomUser.objects.filter(email=email)
        if known_username.exists():
            if (known_username.first().email != email):
                raise serializers.ValidationError()
        if known_email.exists():
            if (known_email.first().username != username):
                raise serializers.ValidationError()
        return data


class RegisterSerializer(serializers.ModelSerializer):
    username_validator = RegexValidator(
        regex=r'^[\w.@+-]+\Z',
        message="Неверный формат Username",
    )
    username = serializers.CharField(validators=[username_validator,
                                                 MinLengthValidator(3),
                                                 MaxLengthValidator(150)],
                                     required=True,
                                     )
    email = serializers.EmailField(max_length=150, required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email')

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        if CustomUser.objects.filter(email=email, username=username).exists():
            return data
        elif (CustomUser.objects.filter(email=email).exists()
              and CustomUser.objects.filter(username=username).exists()):
            raise serializers.ValidationError('Имя и почта с такими значениями заняты')
        elif CustomUser.objects.filter(email=email).exists():
            raise serializers.ValidationError('Такая почта уже занята')
        elif CustomUser.objects.filter(username=username):
            raise serializers.ValidationError('Такое имя уже занято')
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
        fields = ['id', 'name', 'slug']

    def validate_name(self, value):
        if len(value) > 256:
            raise serializers.ValidationError(
                "Название не должно быть длиннее 256 символов."
            )
        return value

    def validate_slug(self, value):
        if len(value) > 50:
            raise serializers.ValidationError(
                "Slug не должен быть длиннее 50 символов."
            )
        if not re.match(r'^[-a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError(
                "Slug содержит недопустимые символы."
            )
        return value


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name', 'slug']


class TitleSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Title
        fields = ['id', 'name', 'year', 'genre', 'category']
