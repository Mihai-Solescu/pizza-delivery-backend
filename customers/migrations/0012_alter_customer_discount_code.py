# Generated by Django 5.1.1 on 2024-10-12 19:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0011_alter_customer_discount_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='discount_code',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]