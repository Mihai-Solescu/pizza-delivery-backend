import time
from datetime import datetime, timedelta, timezone

from django.db import models

class Delivery(models.Model):
    delivery_id = models.AutoField(primary_key=True)
    delivery_person_id = models.ForeignKey('delivery.DeliveryPerson', on_delete=models.SET_NULL, related_name="deliveries", null=True) #We want to access this from the DeliveryPerson
    delivery_status = models.CharField(max_length=100)
    pizza_quantity = models.IntegerField(default=0)
    delivery_address = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.delivery_status == 'completed':
                self.delivery_person_id.last_dispatched = timezone.now()
                self.delivery_person_id.save()
        super().save(*args, **kwargs)

class DeliveryPerson(models.Model):
    delivery_person_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    last_dispatched = models.DateTimeField(null=True, blank=True)
    postal_area = models.CharField(max_length=30)

    def delivery_person_is_available(self):
        if self.last_dispatched is None:
            return True
        if self.last_dispatched:
            return self.last_dispatched < timezone.now() + timedelta(minutes=30)

