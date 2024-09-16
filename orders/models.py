from django.db import models
from customers.models import Customer
from menu.models import MenuItem
from menu.models import Ingredient
# Create your models here.

class Order(models.Model):
    customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE)
    order_date = models.DateField()
    status = models.CharField(max_length=50)
    total_price = models.DecimalField(decimal_places=3, max_digits=8)
    discount_applied = models.BooleanField(default=False)
    delivery_address = models.CharField(max_length=30)


class OrderMenuItem(models.Model):
    order = models.ForeignKey(Order, related_name='order_menu_items', on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.IntegerField()


class OrderMenuItemExtraIngredient(models.Model):
    order_menu_item = models.ForeignKey(OrderMenuItem, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.IntegerField()


