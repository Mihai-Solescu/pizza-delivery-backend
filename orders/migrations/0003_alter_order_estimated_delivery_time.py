# Generated by Django 5.1.1 on 2024-09-16 21:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_order_estimated_delivery_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='estimated_delivery_time',
            field=models.DurationField(blank=True, null=True),
        ),
    ]