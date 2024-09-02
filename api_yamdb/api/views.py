# Django
from django.conf import settings

# Standard library
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.db.models import Avg

# Third-party
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, views, permissions, filters
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework import mixins, viewsets

# Local
from reviews.models import CustomUser, Title, Comment, Review, Category, Genre
from api.serializers import (RegisterSerializer,
                             UserSerializer,
                             CategorySerializer,
                             GenreSerializer,
                             TokenSerializer,
                             CommentSerializer,
                             ReviewSerializer)
from .serializers import TitleGetSerializer, TitlePostSerializer
from .permissions import (IsAdmin,
                          IsReadOnly,
                          AdminModeratorAuthor)
from .filters import TitleFilter


class BaseViewSet(viewsets.GenericViewSet):
    permission_classes = (IsAdmin,)
    http_method_names = ('get', 'post', 'delete', 'head', 'options')
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('name',)

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return (IsReadOnly(), )
        return (IsAdmin(), )


class CategoryViewSet(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      BaseViewSet):
    queryset = Category.objects.order_by('id')
    serializer_class = CategorySerializer
    lookup_field = 'slug'

    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class GenreViewSet(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.DestroyModelMixin,
                   BaseViewSet):
    queryset = Genre.objects.all().order_by('id')
    serializer_class = GenreSerializer
    lookup_field = 'slug'

    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')).all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsReadOnly()]
        return [IsAdmin()]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TitleGetSerializer
        return TitlePostSerializer

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=True)
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
    search_fields = ('username', 'email',)
    pagination_class = PageNumberPagination

    @action(detail=False,
            methods=['GET', 'PATCH'],
            permission_classes=[permissions.IsAuthenticated, ])
    def me(self, request):
        if request.method == 'GET':
            serializer = UserSerializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == 'PATCH':
            serializer = UserSerializer(request.user, data=request.data,
                                        partial=True)
        if request.user.is_admin or request.user.is_moderator:
            serializer.is_valid(raise_exception=True)
            serializer.save()
        else:
            serializer.is_valid(raise_exception=True)
            serializer.save(role=request.user.role)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RegisterView(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user = get_object_or_404(
            CustomUser, username=serializer.validated_data['username'])
        confirmation_code = default_token_generator.make_token(user)
        user.confirmation_code = confirmation_code
        user.save()
        send_mail(
            subject='Успешное создание кода',
            message=f'Код создан, ваш код - {confirmation_code}',
            from_email=settings.DEFAULT_FROM_EMAIL,  # Переносим в settings.py
            recipient_list=[user.email, ],
            fail_silently=True
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenView(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
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


class ReviewViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = (AdminModeratorAuthor,)

    def get_title(self):
        return get_object_or_404(Title,
                                 pk=self.kwargs.get('title_id'))

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=self.get_title()
        )

    def get_queryset(self):
        return self.get_title().reviews.all()


class CommentViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (AdminModeratorAuthor,)

    def get_review(self):
        return get_object_or_404(
            Review, pk=self.kwargs.get('review_id'),
            title__id=self.kwargs.get('title_id'))

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            review=self.get_review(),
        )

    def get_queryset(self):
        return self.get_review().comments.all()
