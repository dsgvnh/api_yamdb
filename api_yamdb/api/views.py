from django.shortcuts import render

from rest_framework import viewsets
from reviews.models import Category, Genre, Title, CustomUser
from .serializers import (CategorySerializer, GenreSerializer,
                          TitleSerializer, RegisterSerializer)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer


class UsersViewSet(viewsets.ModelViewSet):
    ''' Нужно доработать (а может и не нужно - надо смотреть тесты)'''
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer