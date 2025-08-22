from rest_framework import generics, permissions, status
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
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

        try:
            product = Product.objects.get(id=request.data.get('product_id'))
        except Product.DoesNotExist:
            return Response({"error": "No product with this id"})
        
        cart_item, _ = CartItem.objects.get_or_create(cart=cart, product=product)
        cart_item.quantity += int(request.data.get('quantity', 1))
        cart_item.save()
        return Response(
            CartItemSerializer(cart_item).data,
            status=status.HTTP_201_CREATED
        )

    
class CartItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CartItemSerializer
    permission_class = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(cart_user=self.request.user)
#----------------------------- ORDER ENDPOINTS-------------------------------------------
class OrderItemCreateView(generics.CreateAPIView):
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        order, _ = Order.objects.get_or_create(user=self.request.user)

        try:
            product = Product.objects.get(id=request.data.get('product_id'))
        except Product.DoesNotExist:
            return Response({"error": "No product with this id"})
        
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        
        print(created)
        if created == True:
            quantity = int(1)
        else:
            quantity = int(cart_item.quantity)
        
        price = float(product.price) * quantity
        
        order_item = OrderItem.objects.create(order=order, product=product, quantity=quantity, price=price)
        order_item.save()
        return Response(
            OrderItemSerializer(order_item).data,
            status=status.HTTP_201_CREATED
        )
    
class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_class = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
