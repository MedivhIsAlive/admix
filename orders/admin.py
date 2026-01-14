from django.contrib import admin
from orders.models import Order, OrderItem1, OrderItem2

# Register your models here.
admin.register(Order)
admin.register(OrderItem1)
admin.register(OrderItem2)
