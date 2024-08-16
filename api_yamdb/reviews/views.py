# В доработке!
from rest_framework import generics, viewsets
from api.serializers import RegisterSerializer
from .models import CustomUser


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

class TokenView(generics.CreateAPIView):
    pass
