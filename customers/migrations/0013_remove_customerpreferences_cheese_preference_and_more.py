# Generated by Django 5.1.1 on 2024-10-13 08:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0012_alter_customer_discount_code'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customerpreferences',
            name='cheese_preference',
        ),
        migrations.RemoveField(
            model_name='customerpreferences',
            name='favourite_sauce',
        ),
        migrations.RemoveField(
            model_name='customerpreferences',
            name='pizza_size',
        ),
        migrations.RemoveField(
            model_name='customerpreferences',
            name='spiciness_level',
        ),
        migrations.AddField(
            model_name='customerpreferences',
            name='cheesy',
            field=models.DecimalField(decimal_places=3, default=1, max_digits=8),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='customerpreferences',
            name='is_meat',
            field=models.DecimalField(decimal_places=3, default=1, max_digits=8),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='customerpreferences',
            name='is_vegetable',
            field=models.DecimalField(decimal_places=3, default=1, max_digits=8),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='customerpreferences',
            name='salty',
            field=models.DecimalField(decimal_places=3, default=1, max_digits=8),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='customerpreferences',
            name='spicy',
            field=models.DecimalField(decimal_places=3, default=1, max_digits=8),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='customerpreferences',
            name='sweet',
            field=models.DecimalField(decimal_places=3, default=1, max_digits=8),
            preserve_default=False,
        ),
    ]
