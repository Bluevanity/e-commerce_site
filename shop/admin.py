from django.contrib import admin
from .models import CustomUser, Product, Cart, CartItem, Order, OrderItem
# Register your models here.

admin.site.register(CustomUser)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(OrderItem)