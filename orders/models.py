from datetime import datetime, timedelta
from django.db import models
from decimal import Decimal
from django.utils import timezone
from customers.models import Customer
from delivery.models import Delivery
from menu.models import Ingredient, Dessert, Drink, Pizza

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_date = models.DateField()
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('confirmed', 'Confirmed'),
        ('delivering', 'Delivering'),
        ('delivered', 'Delivered'),
        ('canceled', 'Canceled'),
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="open")
    delivery = models.ForeignKey('delivery.Delivery', blank=True, null=True, on_delete=models.CASCADE)
    discount_applied = models.BooleanField(default=False)
    freebie_applied = models.BooleanField(default=False)
    estimated_delivery_time = models.IntegerField(blank=True, null=True)

    def apply_loyalty_discount(self):
        """Applies a 10% loyalty discount if the customer has ordered more than 10 pizzas."""
        if self.customer.total_pizzas_ordered >= 10:
            self.customer.total_pizzas_ordered -= 10
            self.customer.discount_applied = True
            self.customer.save()
            self.discount_applied = True

    def apply_discount_code(self):
        """Applies a discount code if available and not redeemed."""
        if self.customer.discount_code and not self.customer.discount_code.is_redeemed:
            self.customer.discount_code.is_redeemed = True
            self.customer.discount_applied = True
            self.discount_applied = True
            self.customer.save()

    def apply_birthday_freebies(self):
        """Applies a free pizza and drink if it's the customer's birthday and they haven't received a freebie yet."""
        today = timezone.now().date()
        if self.customer.birthdate.month == today.month and self.customer.birthdate.day == today.day and not self.customer.is_birthday_freebie:
            pizza_free = False
            drink_free = False
            for item in self.items.all():
                if item.content_type == 'pizza' and not pizza_free:
                    pizza_free = True
                elif item.content_type == 'drink' and not drink_free:
                    drink_free = True
                if pizza_free and drink_free:
                    self.customer.is_birthday_freebie = True
                    self.customer.save()
                    break
            self.freebie_applied = True

    def calculate_estimated_delivery_time(self):
        """Calculates estimated delivery time based on the number of pizzas ordered."""
        pizza_items = self.items.filter(content_type='pizza')
        pizza_quantity = sum([item.quantity for item in pizza_items])
        self.estimated_delivery_time = pizza_quantity * 2 + 10

    def calculate_total_price(self):
        """
        Calculate the total price, applying any discounts and freebies.
        The most expensive pizza will be free if it's a birthday freebie.
        """
        total_price = Decimal('0.00')
        pizzas = self.items.filter(content_type='pizza')

        # Find the most expensive pizza
        if pizzas.exists():
            most_expensive_pizza = max(pizzas, key=lambda item: item.get_price())
            if self.freebie_applied:
                pizzas = pizzas.exclude(id=most_expensive_pizza.id)

        for item in self.items.all():
            total_price += item.get_price() * item.quantity

        # Apply loyalty discount or discount code (10%)
        if self.discount_applied:
            total_price *= Decimal('0.9')

        return round(total_price, 2)

    def add_menu_item(self, item, quantity):
        """Add an item (pizza, drink, or dessert) to the order."""
        if isinstance(item, Pizza):
            item_type = 'pizza'
            object_id = item.pizza_id
        elif isinstance(item, Drink):
            item_type = 'drink'
            object_id = item.drink_id
        elif isinstance(item, Dessert):
            item_type = 'dessert'
            object_id = item.dessert_id
        else:
            raise ValueError('Invalid item type')

        order_item, created = OrderItem.objects.get_or_create(
            order=self,
            content_type=item_type,
            object_id=object_id,
            defaults={'quantity': quantity}
        )

        if not created:
            order_item.quantity += quantity
            order_item.save()

    def update_customer_pizza_count(self):
        """Update the total number of pizzas ordered by the customer."""
        pizza_items = self.items.filter(content_type='pizza')
        pizza_quantity = sum([item.quantity for item in pizza_items])
        self.customer.total_pizzas_ordered += pizza_quantity
        self.customer.save()

    def process_order(self):
        """Process the order by applying discounts, freebies, calculating the delivery time, and confirming the order."""
        if self.status == 'open':
            self.apply_loyalty_discount()
            self.apply_discount_code()
            self.apply_birthday_freebies()
            self.calculate_estimated_delivery_time()
            self.update_customer_pizza_count()
            self.status = 'confirmed'
            self.save()
        else:
            raise ValueError('Order is not open')

    def cancel_order_within_time(self):
        """Allow the order to be canceled if it's within 5 minutes of order placement."""
        if self.order_date < datetime.now() + timedelta(minutes=5):
            self.status = "canceled"
            self.save()
            return True
        else:
            return False




class OrderItem(models.Model):
    ITEM_TYPES = [
        ('pizza', 'Pizza'),
        ('drink', 'Drink'),
        ('dessert', 'Dessert'),
    ]

    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='items')
    content_type = models.CharField(max_length=50, choices=ITEM_TYPES)
    object_id = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField(default=1)
