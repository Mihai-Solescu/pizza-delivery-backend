# delivery/models.py

from django.db import models
from django.utils import timezone
from datetime import timedelta

class DeliveryPerson(models.Model):
    delivery_person_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    last_dispatched = models.DateTimeField(null=True, blank=True)
    postal_area = models.CharField(max_length=30)

    def delivery_person_is_available(self):
        if self.last_dispatched is None:
            return True
        return self.last_dispatched + timedelta(minutes=30) <= timezone.now()

class Delivery(models.Model):
    delivery_id = models.AutoField(primary_key=True)
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_process', 'In Process'),
        ('completed', 'Completed'),
        ('no_courier', 'No Courier'),
    ]
    delivery_person = models.ForeignKey(
        'DeliveryPerson',
        on_delete=models.SET_NULL,
        related_name="deliveries",
        null=True
    )
    delivery_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    pizza_quantity = models.IntegerField(default=0)
    delivery_postal_code = models.CharField(max_length=100)
    delivery_address = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

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
            self.delivery_status = 'in_process'
            self.save()
            return True
        else:
            return False