from django.contrib import admin

# Register your models here.

from .models import Customer, UserPreferences

admin.site.register(Customer)
admin.site.register(UserPreferences)