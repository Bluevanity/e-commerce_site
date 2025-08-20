from rest_framework import generics
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, ProductSerializer
from .models import IsAdminUser, Product

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAdminUser]
    serializer_class = RegisterSerializer

class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    permission_classes = (AllowAny)
    serializer_class = ProductSerializer