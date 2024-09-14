from django.db import models

class Delivery(models.Model):
    delivery_id = models.AutoField(primary_key=True)
    order_id = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True)
    delivery_person_id = models.ForeignKey('delivery.DeliveryPerson', on_delete=models.SET_NULL, related_name="deliveries", null=True) #We want to access this from the DeliveryPerson
    delivery_status = models.CharField(max_length=100)
    estimated_delivery_time = models.TimeField()

class DeliveryPerson(models.Model):
    delivery_person_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    is_available = models.BooleanField(default=True)  # Is this a good default?
    delivery_address = models.CharField(max_length=30)
