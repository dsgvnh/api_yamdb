from rest_framework import serializers
from reviews.models import Category, Genre, Title
from reviews.models import CustomUser
import re


class RegisterSerializer(serializers.ModelSerializer):
    # В этот класс нужно дописать валидацию на имя и фамилию - требуют тесты
    class Meta:
        model = CustomUser
        fields = ('username', 'email', )

    def create(self, validated_data):
        user = CustomUser(**validated_data)
        user.save()
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
