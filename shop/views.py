from rest_framework import generics
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from rest_framework import permissions
from rest_framework.response import Response
from .serializers import RegisterSerializer, ProductSerializer, OrderItemSerializer, OrderSerializer, CartItemSerializer, CartSerializer
from .models import IsAdminUser, Product, OrderItem, Order, Cart, CartItem

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [IsAdminUser]

#----------------------------- PRODUCT ENDPOINTS-------------------------------------------

class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]
    

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAdminUser()]  # only admins can modify
        return [permissions.AllowAny()]
    
#----------------------------- CART ENDPOINTS-------------------------------------------

class CartDetailView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_class = [permissions.IsAuthenticated]

    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart
    
class CartItemCreateView(generics.CreateAPIView):
    serializer_class = CartItemSerializer
    permission_class = [permissions.IsAuthenticated]

    def create(self, request):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        product_id = request.data.get('product_id')
        quntity = request.data.get('quantity')

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "No product with this id"})
#----------------------------- ORDER ENDPOINTS-------------------------------------------
class OrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]
    lookup_field = User

class OrderDetailView(generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    parser_classes = [AllowAny]

