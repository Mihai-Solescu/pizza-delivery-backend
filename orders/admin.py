from django.contrib import admin
from .models import Order, OrderMenuItem, OrderMenuItemExtraIngredient
# Register your models here.

admin.site.register(Order)
admin.site.register(OrderMenuItem)
admin.site.register(OrderMenuItemExtraIngredient)