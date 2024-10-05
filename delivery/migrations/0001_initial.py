# Generated by Django 5.1.1 on 2024-10-05 17:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeliveryPerson',
            fields=[
                ('delivery_person_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=30)),
                ('is_available', models.BooleanField(default=True)),
                ('postal_area', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Delivery',
            fields=[
                ('delivery_id', models.AutoField(primary_key=True, serialize=False)),
                ('delivery_status', models.CharField(max_length=100)),
                ('order_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='orders.order')),
                ('delivery_person_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='deliveries', to='delivery.deliveryperson')),
            ],
        ),
    ]
