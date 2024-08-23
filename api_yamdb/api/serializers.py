from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from reviews.models import Category, Genre, Title, CustomUser
from django.core.validators import (RegexValidator, MaxLengthValidator,
                                    MinLengthValidator)


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=150,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Username должен содержать только буквы, цифры и символы: @ . + -',
                code='invalid_username'
            )
        ],
        required=True,)
    confirmation_code = serializers.CharField(required=True)


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


class RegisterSerializer(serializers.Serializer):
    username_validator = RegexValidator(
        regex=r'^[\w.@+-]+\Z',
        message="Неверный формат Username",
    )
    username = serializers.CharField(validators=[username_validator,
                                                 MinLengthValidator(3),
                                                 MaxLengthValidator(150)],
                                     required=True,
                                     )
    email = serializers.EmailField(max_length=254, required=True)

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        if CustomUser.objects.filter(email=email, username=username).exists():
            return data
        elif (CustomUser.objects.filter(email=email).exists()
              and CustomUser.objects.filter(username=username).exists()):
            raise serializers.ValidationError({'email': 'Такая почта уже занята',
                                              'username': 'Такое имя уже занято'})
        elif CustomUser.objects.filter(email=email).exists():
            raise serializers.ValidationError({'email': 'Такая почта уже занята'})
        elif CustomUser.objects.filter(username=username):
            raise serializers.ValidationError({'username': 'Такое имя уже занято'})
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
        fields = ['name', 'slug']



class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['name', 'slug']


class TitlePostSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field='slug', queryset=Category.objects.all())
    genre = serializers.SlugRelatedField(slug_field='slug', queryset=Genre.objects.all(), many=True)

    class Meta:
        model = Title
        fields = '__all__'

    def to_representation(self, instance):
        return TitleGetSerializer(instance).data

class TitleGetSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Title
        fields = '__all__'