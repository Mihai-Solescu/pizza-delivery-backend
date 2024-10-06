from django.db import models
from decimal import Decimal
from django.utils import timezone
from customers.models import Customer
from menu.models import Ingredient, Dessert, Drink, Pizza


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_date = models.DateField()
    status = models.CharField(max_length=50, default="pending")
    total_price = models.DecimalField(decimal_places=3, max_digits=8, default=Decimal('0.00'))
    discount_applied = models.BooleanField(default=False)
    delivery_address = models.CharField(max_length=255)
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
        if self.customer.birthdate.month == today.month and self.customer.birthdate.day == today.day and not self.customer.is_birthday_freebie:
            pizza_free = False
            drink_free = False
            for item in self.order_menu_items.all():
                if item.menu_item.type == 'pizza' and not pizza_free:
                    self.total_price -= item.menu_item.price
                    pizza_free = True
                elif item.menu_item.type == 'drink' and not drink_free:
                    self.total_price -= item.menu_item.price
                    drink_free = True
                if pizza_free and drink_free:
                    self.customer.is_birthday_freebie = True
                    self.customer.save()
                    break
            self.discount_applied = True

    def calculate_estimated_delivery_time(self):
        pizza_items = self.order_menu_items.filter(menu_item__type='pizza')
        pizza_quantity = sum([item.quantity for item in pizza_items])
        self.estimated_delivery_time = pizza_quantity * 2 + 10


    def add_menu_item(self, item, quantity):
        # Determine item type and id
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
        pizza_items = self.order_menu_items.filter(menu_item__type='pizza')
        pizza_quantity = sum([item.quantity for item in pizza_items])
        self.customer.total_pizzas_ordered += pizza_quantity
        self.customer.save()

    def process_order(self):
        self.apply_loyalty_discount()
        self.apply_discount_code()
        self.apply_birthday_freebies()
        self.calculate_estimated_delivery_time()
        self.update_customer_pizza_count()
        self.status = 'confirmed'
        self.save()

class OrderItem(models.Model):
    ITEM_TYPES = [
        ('pizza', 'Pizza'),
        ('drink', 'Drink'),
        ('dessert', 'Dessert'),
    ]

    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='items')
    content_type = models.CharField(max_length=50, choices=ITEM_TYPES)
    object_id = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.content_type} (ID: {self.object_id})"
