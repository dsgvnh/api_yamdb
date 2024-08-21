from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (CategoryViewSet, GenreViewSet, TitleViewSet,
                    UsersViewSet, RegisterView, TokenView)


router_v1 = DefaultRouter()

router_v1.register(r'titles', TitleViewSet, basename='titles')
router_v1.register(r'categories', CategoryViewSet, basename='categories')
router_v1.register(r'genres', GenreViewSet, basename='genres')
router_v1.register(r'users', UsersViewSet, basename='users')

urlpatterns = [
    path('v1/auth/signup/', RegisterView.as_view()),
    path('v1/auth/token/', TokenView.as_view()),
    path('v1/', include(router_v1.urls)),
]
