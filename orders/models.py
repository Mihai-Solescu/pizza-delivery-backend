import datetime
from decimal import Decimal
from time import timezone

from django.db import models
from customers.models import Customer
from menu.models import Ingredient
# Create your models here.

class Order(models.Model):
    customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE)
    order_date = models.DateField()
    status = models.CharField(max_length=50, default="open")
    total_price = models.DecimalField(decimal_places=3, max_digits=8)
    discount_applied = models.BooleanField(default=False)
    delivery_address = models.CharField(max_length=30)
    estimated_delivery_time = models.IntegerField(blank=True, null=True)

    def apply_loyalty_discount(self):
        if self.customer.total_pizzas_ordered >= 10:
            self.total_price *= Decimal('0.9')
            self.customer.total_pizzas_ordered -= 10
            self.customer.save()
            self.discount_applied = True

    def apply_discount_code(self):
        if self.customer.discount_code and not self.customer.discount_code.is_redeemed:
            self.total_price *= Decimal('0.9')
            self.customer.discount_code.is_redeemed = True
            self.customer.discount_code.save()
            self.discount_applied = True

    def apply_birthday_freebies(self):
        today = timezone.now().date()
        if (self.customer.birthdate.month == today.month and self.customer.birthdate.day == today.day
                and not self.customer.is_birthday_freebie):
            pizza_free = False
            drink_free = False
            for item in self.order_menu_items.all():
                if item.type == 'pizza' and not pizza_free:
                    self.total_price -= item.price
                    pizza_free = True
                elif item.type == 'drink' and not drink_free:
                    self.total_price -= item.price
                    drink_free = True
                if pizza_free and drink_free:
                    self.customer.is_birthday_freebie = True
                    self.customer.save()
                    break
            self.discount_applied = True

    def calculate_estimated_delivery_time(self):
        pizza_items = self.order_menu_items.filter(type='pizza')
        pizza_amount = sum([item.quantity for item in self.ordermenuitem_set.filter(menu_item__in=pizza_items)])
        self.estimated_delivery_time = pizza_amount * 2 + 10

    def update_customer_pizza_count(self):
        pizza_items = self.order_menu_items.filter(type='pizza')
        pizza_quantity = sum([item.quantity for item in self.ordermenuitem_set.filter(menu_item__in=pizza_items)])
        self.customer.total_pizzas_ordered += pizza_quantity
        self.customer.save()

    def process_order(self):
        self.apply_loyalty_discount()
        self.apply_discount_code()
        self.apply_birthday_freebies()
        self.calculate_estimated_delivery_time()
        self.update_customer_pizza_count()
        self.save()


class OrderMenuItem(models.Model):
    order = models.ForeignKey(Order, related_name='order_menu_items', on_delete=models.CASCADE)
    quantity = models.IntegerField()


class OrderMenuItemExtraIngredient(models.Model):
    order_menu_item = models.ForeignKey(OrderMenuItem, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.IntegerField()


