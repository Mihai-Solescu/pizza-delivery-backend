from django.contrib import admin

# Register your models here.

from .models import Customer, DiscountCode

admin.site.register(Customer)
admin.site.register(DiscountCode)