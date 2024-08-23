from rest_framework import viewsets, status, views, permissions, filters
from rest_framework.response import Response
from api.serializers import (RegisterSerializer, TokenSerializer,
                             UserSerializer, CategorySerializer,
                             GenreSerializer)
from reviews.models import CustomUser, Category, Genre, Title
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from .permissions import IsAdmin
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from .permissions import IsAdminOrReadOnly
from .serializers import TitleGetSerializer, TitlePostSerializer
from .filters import WriteFilter
from rest_framework import viewsets
from reviews.models import Title
from rest_framework import permissions

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = WriteFilter

    def get_serializer_class(self):
        if self.action == 'list':
            return TitleGetSerializer
        return TitlePostSerializer

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(isinstance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated, IsAdmin)
    http_method_names = ['get', 'post', 'patch', 'delete']
    lookup_field = 'username'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ('username', 'email', )
    pagination_class = PageNumberPagination

    @action(detail=False,
            methods=['GET', 'PATCH'],
            permission_classes=[permissions.IsAuthenticated, ])
    def me(self, request):
        serializer = UserSerializer(request.user,
                                    data=request.data,
                                    partial=True)
        if request.user.role == 'admin' or request.user.role == 'moderator':
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer.is_valid(raise_exception=True)
        serializer.save(role='user')
        return Response(serializer.data, status=status.HTTP_200_OK)


class RegisterView(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user = CustomUser.objects.get(username=serializer.validated_data['username'])
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            subject='Успешное создание кода',
            message=f'Код создан, ваш код - {confirmation_code}',
            from_email='api@yamdb.ru',
            recipient_list=[user.email, ],
            fail_silently=True
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenView(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwagrs):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        confirmation_code = serializer.validated_data.get('confirmation_code')
        user = get_object_or_404(CustomUser, username=username)
        if default_token_generator.check_token(user, confirmation_code):
            token = AccessToken.for_user(user)
            message = {'token': str(token)}
            return Response(message, status=status.HTTP_200_OK)
        else:
            return Response(request.data, status=status.HTTP_400_BAD_REQUEST)
