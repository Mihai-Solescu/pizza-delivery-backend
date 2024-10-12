from django.contrib import admin

# Register your models here.

from .models import Customer, CustomerPreferences

admin.site.register(Customer)
admin.site.register(CustomerPreferences)