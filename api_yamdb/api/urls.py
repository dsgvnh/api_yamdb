from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, GenreViewSet, TitleViewSet, UsersViewSet
from reviews.views import RegisterView, TokenView

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'genres', GenreViewSet)
router.register(r'titles', TitleViewSet)
router.register(r'users', UsersViewSet)  # по тестам не проходит - надо переписывать


urlpatterns = [
    path('v1/auth/signup/', RegisterView.as_view()),
    path('v1/auth/token/', TokenView.as_view()),  # Не работает
    path('v1/', include(router.urls)),
]
