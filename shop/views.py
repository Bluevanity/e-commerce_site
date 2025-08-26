import stripe
import os
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework import generics, permissions, status
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from .serializers import RegisterSerializer, ProductSerializer, OrderItemSerializer, OrderSerializer, CartItemSerializer, CartSerializer
from .models import IsAdminUser, Product, OrderItem, Order, Cart, CartItem

User = get_user_model()
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
endpoint_secret = os.getenv("STRIPE_ENDPOINT_SECRET")  # from Stripe dashboard

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']

    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return HttpResponse(status=400)  
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)  # Invalid signature

    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        order_id = payment_intent['metadata'].get('order_id')  # we’ll pass this when creating intent
        if order_id:
            try:
                order = Order.objects.get(id=order_id)
                order.status = "Successful"
                order.save()
                print(f"Order {order.id} marked as Successful")
            except Order.DoesNotExist:
                print(" Order not found")

    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        order_id = payment_intent['metadata'].get('order_id')
        if order_id:
            try:
                order = Order.objects.get(id=order_id)
                order.status = "Failed"
                order.save()
                print(f"Order {order.id} marked as Failed")
            except Order.DoesNotExist:
                print("Order not found")

    return HttpResponse(status=200)

#-------------------------------------------------------------------------------------------
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

    def create(self, request, *args, **kwargs):
        user = self.request.user

        # Get or create cart for user
        cart, _ = Cart.objects.get_or_create(user=user)

        # Always tie new items to a "Pending" order
        order, created_now = Order.objects.get_or_create(user=user, status="Pending")

        # Check product exists
        try:
            product = Product.objects.get(id=request.data.get("product_id"))
        except Product.DoesNotExist:
            return Response({"error": "No product with this id"}, status=status.HTTP_400_BAD_REQUEST)

        # Add or update cart item
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if created:
            cart_item.quantity = 1
        cart_item.save()

        # Calculate price for this order item
        price = product.price * cart_item.quantity

        # If order item already exists, update instead of creating duplicate
        order_item, created_item = OrderItem.objects.get_or_create(order=order, product=product)

        order_item.quantity = cart_item.quantity
        order_item.price = price
        order_item.save()

        # Update total amount
        order.total_amount = sum(item.price for item in order.orderitem_set.all())
        order.save()

        return Response(
            OrderItemSerializer(order_item).data,
            status=status.HTTP_201_CREATED,
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

#------------------------------------------------------------------------------------------

stripe.api_key = settings.STRIPE_SECRET_KEY

class CreateStripePaymentIntent(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            # Example: total from request payload
            #amount = request.data.get("amount")  # in cents, e.g. 2000 = $20
            amount = request.user.order_set.filter(status="Pending").first().total_amount 
            if not amount:
                return Response({"error": "Amount is required"}, status=status.HTTP_400_BAD_REQUEST)

            intent = stripe.PaymentIntent.create(
                amount=int(amount),
                currency="usd",
                automatic_payment_methods={"enabled": True},
                metadata={"user_id": request.user.id}  # optional
            )

            return Response({
                "clientSecret": intent["client_secret"]
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)