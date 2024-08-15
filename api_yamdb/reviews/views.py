# accounts/views.py

from rest_framework import generics
from api.serializers import RegisterSerializer

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

class TokenObtainPairView(generics.GenericAPIView):
    # Здесь вы можете использовать стандартный класс или создать свой
    pass  # Реализуйте получение токена по своему усмотрению
