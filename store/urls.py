"""
URL configuration for store project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from shop.views import (
    RegisterView, 
    UserListView, 
    ProductListCreateView, 
    ProductDetailView, 
    CartDetailView,
    CartItemCreateView,
    CartDetailView,
    OrderItemCreateView,
    OrderListView,
    OrderDetailView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', TokenObtainPairView.as_view(), name='login'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/users/', UserListView.as_view(), name='users'), #locked endpoint
    path('api/products/', ProductListCreateView.as_view(), name='products'), #locked post endpoint
    path('api/products/<pk>/', ProductDetailView.as_view(), name='product_detail'), #locked put, patch, delelet endpoint
    path('api/cart/',  CartDetailView.as_view(), name='cart_detail'),
    path('api/cart/add',  CartItemCreateView.as_view(), name='add_item'),
    path('api/cart/update/<pk>/', CartDetailView.as_view(), name='update_item'),
    path('api/order/', OrderItemCreateView.as_view(), name='make_order'),
    path('api/orders/', OrderListView.as_view(), name="orders"),
    path('api/orders/<pk>/', OrderDetailView.as_view(), name='order_detail'),

]

