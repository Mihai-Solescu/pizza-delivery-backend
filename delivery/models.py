import time
from datetime import datetime, timedelta, timezone

from django.db import models

class Delivery(models.Model):
    delivery_id = models.AutoField(primary_key=True)
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_process', 'In Process'),
        ('completed', 'Completed'),
    ]
    delivery_person_id = models.ForeignKey('delivery.DeliveryPerson', on_delete=models.SET_NULL, related_name="deliveries", null=True) #We want to access this from the DeliveryPerson
    delivery_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    pizza_quantity = models.IntegerField(default=0)
    delivery_postal_code = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        if self.delivery_status == 'in_process' and self.delivery_person:
            self.delivery_person.last_dispatched = timezone.now()
            self.delivery_person.save()
        super().save(*args, **kwargs)

    def assign_delivery_person(self):
        available_delivery_persons = DeliveryPerson.objects.filter(
            postal_area=self.delivery_postal_code
        ).filter(
            models.Q(last_dispatched__isnull=True) |
            models.Q(last_dispatched__lte=timezone.now() - timedelta(minutes=30))
        )

        if available_delivery_persons.exists():
            self.delivery_person = available_delivery_persons.first()
            self.save()
            return True
        else:
            return False

class DeliveryPerson(models.Model):
    delivery_person_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    last_dispatched = models.DateTimeField(null=True, blank=True)
    postal_area = models.CharField(max_length=30)

    def delivery_person_is_available(self):
        if self.last_dispatched is None:
            return True
        return self.last_dispatched + timedelta(minutes=30) <= timezone.now()

