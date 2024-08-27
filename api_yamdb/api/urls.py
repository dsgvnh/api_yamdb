from django.urls import include, path  # Импорты из библиотеки Django

from rest_framework.routers import DefaultRouter  # Импорты сторонних библиотек

from .views import (  # Импорты модулей текущего проекта
    CategoryViewSet, GenreViewSet, TitleViewSet,
    UsersViewSet, RegisterView, TokenView,
    CommentViewSet, ReviewViewSet
)


router_v1 = DefaultRouter()

router_v1.register('titles', TitleViewSet, basename='titles')
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('users', UsersViewSet, basename='users')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='reviews')


urlpatterns = [
    path('v1/auth/signup/', RegisterView.as_view()),
    path('v1/auth/token/', TokenView.as_view()),
    path('v1/', include(router_v1.urls)),
]
