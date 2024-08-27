from django.urls import include, path  # Импорты из библиотеки Django

from rest_framework.routers import DefaultRouter  # Импорты сторонних библиотек

from .views import (  # Импорты модулей текущего проекта
    CategoryViewSet, GenreViewSet, TitleViewSet,
    UsersViewSet, RegisterView, TokenView,
    CommentViewSet, ReviewViewSet
)



router_v1 = DefaultRouter()

router_v1.register(r'titles', TitleViewSet)
router_v1.register(r'categories', CategoryViewSet)
router_v1.register(r'genres', GenreViewSet)
router_v1.register(r'users', UsersViewSet)
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
