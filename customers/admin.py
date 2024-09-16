from django.contrib import admin

# Register your models here.

from .models import Customer, CustomerAddress, DiscountCode

admin.site.register(Customer)
admin.site.register(CustomerAddress)
admin.site.register(DiscountCode)