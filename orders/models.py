from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from delivery.models import Delivery
from customers.models import Customer
from menu.models import Pizza


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_date = models.DateTimeField(null=True, blank=True)
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('confirmed', 'Confirmed'),
        ('delivering', 'Delivering'),
        ('delivered', 'Delivered'),
        ('canceled', 'Canceled'),
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="open")
    delivery = models.ForeignKey(
        'delivery.Delivery',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='orders'
    )

    redeemable_discount_applied = models.BooleanField(default=False)
    loyalty_discount_applied = models.BooleanField(default=False)
    freebie_applied = models.BooleanField(default=False)
    estimated_delivery_time = models.IntegerField(blank=True, null=True, default=30)

    class Meta:
        unique_together = ('customer', 'status')  # Ensures only one open order per customer

    def __str__(self):
        return f"Order {self.id} by {self.customer}"

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
        if self.customer.birthdate is None:
            return
        today = timezone.now().date()
        if (self.customer.birthdate.month == today.month and 
            self.customer.birthdate.day == today.day and 
            not self.customer.is_birthday_freebie):
            self.freebie_applied = True

    def calculate_item_count(self):
        return self.items.count()

    def calculate_total_price(self):
        from decimal import Decimal
        total_price = Decimal('0.00')

        pizzas = []

        items = self.items.all()
        if items.count() == 0:
            return total_price
        for item in items:
            if item.content_type.model == 'pizza':
                total_price += item.content_object.get_price() * item.quantity
                pizzas.append(item.content_object)
            elif item.content_type.model == 'drink':
                total_price += item.content_object.price * item.quantity
            elif item.content_type.model == 'dessert':
                total_price += item.content_object.price * item.quantity
            else:
                raise ValueError('Invalid item type')

        if pizzas:
            most_expensive_pizza = max(pizzas, key=lambda item: item.get_price())
            if self.freebie_applied:
                total_price -= most_expensive_pizza.get_price()
        if self.loyalty_discount_applied:
            total_price *= Decimal('0.9')
        if self.redeemable_discount_applied:
            total_price *= Decimal('0.9')

        return round(total_price, 2)

    def add_menu_item(self, item, quantity):
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
        pizza_content_type = ContentType.objects.get_for_model(Pizza)
        pizza_items = OrderItem.objects.filter(order=self, content_type=pizza_content_type)
        pizza_quantity = sum([item.quantity for item in pizza_items])
        self.customer.total_pizzas_ordered += pizza_quantity
        self.customer.save()
        print(self.customer.total_pizzas_ordered)

    def create_or_update_delivery(self):
        delivery_address = self.customer.address_line
        postal_code = self.customer.postal_code

        three_minutes_ago = timezone.now() - timedelta(minutes=3)
        recent_deliveries = Delivery.objects.filter(
            delivery_postal_code=postal_code,
            delivery_status='pending',
            pizza_quantity__lt=3,
            delivery_person__isnull=False,
            created_at__gte=three_minutes_ago
        )

        for delivery in recent_deliveries:
            if delivery.pizza_quantity + self.get_pizza_quantity() <= 3:
                self.delivery = delivery
                delivery.pizza_quantity += self.get_pizza_quantity()
                delivery.save()
                self.save()
                return

        new_delivery = Delivery.objects.create(
            delivery_status='pending',
            pizza_quantity=self.get_pizza_quantity(),
            delivery_address=delivery_address,
            delivery_postal_code=postal_code
        )

        assigned = new_delivery.assign_delivery_person()
        if not assigned:
            new_delivery.delivery_status = 'no_courier'
            new_delivery.save()
        self.delivery = new_delivery
        self.save()

    def get_pizza_quantity(self):
        pizzas = self.items.filter(content_type__model='pizza')
        return sum(item.quantity for item in pizzas)

    def process_order(self):
        if self.status == 'open':
            self.apply_loyalty_discount()
            self.apply_birthday_freebies()
            self.update_customer_pizza_count()
            self.calculate_estimated_delivery_time()
            self.create_or_update_delivery()
            print('Order processed')
            self.status = 'confirmed'
            self.order_date = timezone.now()
            print('Order confirmed')
            self.save()
            print('Order processed')
        else:
            raise ValueError('Order is not open')

    def calculate_estimated_delivery_time(self):
        pizza_content_type = ContentType.objects.get_for_model(Pizza)
        pizza_items = OrderItem.objects.filter(order=self, content_type=pizza_content_type)
        pizza_quantity = sum([item.quantity for item in pizza_items])
        self.estimated_delivery_time = pizza_quantity * 2 + 10  # Example logic: 2 minutes per pizza + 10 minutes base time

    def cancel_order_within_time(self):
        if not self.order_date:
            return False

        now = timezone.now()
        five_minutes_ago = now - timedelta(minutes=5)
        order_date = self.order_date

        if timezone.is_naive(order_date):
            order_date = timezone.make_aware(order_date, timezone.get_current_timezone())

        if five_minutes_ago <= order_date <= now and self.status in ['open', 'confirmed']:
            self.status = "canceled"
            self.save()
            return True

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
            pizzas = OrderItem.objects.filter(order=order, content_type__model='pizza')
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
        pizzas = OrderItem.objects.filter(order=order, content_type__model='pizza')
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