from datetime import datetime, timedelta

from django.db import models
from decimal import Decimal
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from customers.models import Customer
from delivery.models import Delivery
from menu.models import Ingredient, Dessert, Drink, Pizza
from django.contrib.contenttypes.models import ContentType


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_date = models.DateField(null=True, blank=True)
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('confirmed', 'Confirmed'),
        ('delivering', 'Delivering'),
        ('delivered', 'Delivered'),
        ('canceled', 'Canceled'),
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="open")
    delivery = models.ForeignKey('delivery.Delivery', blank=True, null=True, on_delete=models.CASCADE)

    redeemable_discount_applied = models.BooleanField(default=False)
    loyalty_discount_applied = models.BooleanField(default=False)
    freebie_applied = models.BooleanField(default=False)
    estimated_delivery_time = models.IntegerField(blank=True, null=True)

    def apply_loyalty_discount(self):
        if self.customer.total_pizzas_ordered >= 10:
            self.customer.total_pizzas_ordered = 0
            self.customer.save()

    def apply_discount_code(self, discount_code):
        if str(self.customer.discount_code) == discount_code and not self.customer.discount_applied:
            self.customer.discount_applied = True
            self.redeemable_discount_applied = True
            self.customer.save()
            print('Discount applied')

    def apply_birthday_freebies(self):
        today = timezone.now().date()
        if (self.customer.birthdate.month == today.month and self.customer.birthdate.day == today.day and not self.customer.is_birthday_freebie):
            self.freebie_applied = True

    def calculate_item_count(self):
        return self.items.count()

    def calculate_total_price(self):
        """
        Calculate the total price, applying any discounts and freebies.
        The most expensive pizza will be free if it's a birthday freebie.
        """
        total_price = Decimal('0.00')

        pizzas = []

        items = self.items.all()
        if(items.count() == 0):
            return total_price
        for item in items:
            if str(item.content_type) == 'Menu | pizza':
                total_price += item.content_object.get_price() * item.quantity
                pizzas.append(item.content_object)
            elif str(item.content_type) == 'Menu | drink':
                total_price += item.content_object.price * item.quantity
            elif str(item.content_type) == 'Menu | dessert':
                total_price += item.content_object.price * item.quantity
            else:
                raise ValueError('Invalid item type')

        most_expensive_pizza = max(pizzas, key=lambda item: item.get_price())
        if self.freebie_applied:
            total_price -= most_expensive_pizza.get_price()
        if self.loyalty_discount_applied:
            total_price *= Decimal('0.9')
        if self.redeemable_discount_applied:
            total_price *= Decimal('0.9')

        return round(total_price, 2)

    def add_menu_item(self, item, quantity):
        # Determine the content type and object ID for the given item
        content_type = ContentType.objects.get_for_model(item.__class__)
        object_id = item.id

        order_item, created = OrderItem.objects.get_or_create(
            order=self,
            content_type=content_type,
            object_id=object_id,
            defaults={'quantity': quantity}
        )

        if not created:
            order_item.quantity += quantity
            order_item.save()

    def remove_menu_item(self, item, quantity):
        content_type = ContentType.objects.get_for_model(item.__class__)
        object_id = item.id

        order_item = OrderItem.objects.get(
            order=self,
            content_type=content_type,
            object_id=object_id
        )

        if order_item.quantity > quantity:
            order_item.quantity -= quantity
            order_item.save()
        else:
            order_item.delete()

    def update_customer_pizza_count(self):
        pizza_items = OrderItem.objects.filter(order=self, content_type='pizza')
        pizza_quantity = sum([item.quantity for item in pizza_items])
        self.customer.total_pizzas_ordered += pizza_quantity
        self.customer.save()

    def process_order(self):
        if self.status == 'open':
            # discounts
            self.apply_loyalty_discount()
            self.apply_birthday_freebies()
            self.update_customer_pizza_count()
            # delivery
            self.calculate_estimated_delivery_time()
            self.status = 'confirmed'
            self.save()
        else:
            raise ValueError('Order is not open')

    def calculate_estimated_delivery_time(self):
        pizza_items = self.order_menu_items.filter(menu_item__type='pizza')
        pizza_quantity = sum([item.quantity for item in pizza_items])
        self.estimated_delivery_time = pizza_quantity * 2 + 10

    def cancel_order_within_time(self):
        if self.order_date < datetime.now() + timedelta(minutes=5):
            self.status = "cancelled"
            self.save()
            return True
        else:
            return False

    def get_orders_of_past_three_minutes_with_same_address(self):
        three_minutes_ago = timezone.now() - timedelta(minutes=3)
        return Order.objects.filter(
            order_date__gte=three_minutes_ago,
            customer__address_line=self.delivery.delivery_address
        )

    def check_order_combinations(self):
        orders = self.get_orders_of_past_three_minutes_with_same_address()
        for order in orders:
            if order.delivery == self.delivery:
                continue
            pizzas = OrderItem.objects.filter(order=order, content_type='pizza')
            order_pizza_quantity = sum(pizza.quantity for pizza in pizzas)
            combined_pizza_quantity = self.delivery.pizza_quantity + order_pizza_quantity
            if combined_pizza_quantity > 3:
                return False
            self.delivery.pizza_quantity += order_pizza_quantity
            self.delivery.save()
            order.delivery = self.delivery
            order.save()
        return True

    def update_delivery_with_order(self, order):
        pizzas = OrderItem.objects.filter(order=order, content_type='pizza')
        order_pizza_quantity = sum(pizza.quantity for pizza in pizzas)
        self.delivery.pizza_quantity += order_pizza_quantity
        order.delivery = self.delivery
        order.save()
        self.delivery.save()


class OrderItem(models.Model):
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='items')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)  # ForeignKey to ContentType
    object_id = models.PositiveIntegerField()  # ID of the linked object
    content_object = GenericForeignKey('content_type', 'object_id')  # Link to any model (e.g., Pizza, Drink, Dessert)
    quantity = models.PositiveIntegerField(default=1)
