# Generated by Django 5.1.1 on 2024-09-17 07:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_alter_order_estimated_delivery_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='estimated_delivery_time',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]