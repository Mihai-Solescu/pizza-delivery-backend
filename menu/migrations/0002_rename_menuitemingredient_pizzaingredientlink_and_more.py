# Generated by Django 5.1.1 on 2024-10-06 21:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0001_initial'),
        ('orders', '0002_remove_ordermenuitem_menu_item_alter_order_status'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='MenuItemIngredient',
            new_name='PizzaIngredientLink',
        ),
        migrations.RemoveField(
            model_name='pizza',
            name='menu_item_id',
        ),
        migrations.RemoveField(
            model_name='drink',
            name='menu_item',
        ),
        migrations.RemoveField(
            model_name='dessert',
            name='menu_item',
        ),
        migrations.RemoveField(
            model_name='pizza',
            name='base_id',
        ),
        migrations.RemoveField(
            model_name='dessert',
            name='id',
        ),
        migrations.RemoveField(
            model_name='drink',
            name='id',
        ),
        migrations.RemoveField(
            model_name='ingredient',
            name='id',
        ),
        migrations.RemoveField(
            model_name='pizza',
            name='price',
        ),
        migrations.RemoveField(
            model_name='pizza',
            name='time_to_cook',
        ),
        migrations.RemoveField(
            model_name='pizza',
            name='user_id',
        ),
        migrations.AlterUniqueTogether(
            name='pizzaingredientlink',
            unique_together={('pizza', 'ingredient')},
        ),
        migrations.AddField(
            model_name='dessert',
            name='dessert_id',
            field=models.AutoField(default=1, primary_key=True, serialize=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='drink',
            name='drink_id',
            field=models.AutoField(default=1, primary_key=True, serialize=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ingredient',
            name='ingredient_id',
            field=models.AutoField(default=1, primary_key=True, serialize=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ingredient',
            name='is_vegan',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pizzaingredientlink',
            name='pizza',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='menu.pizza'),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='MenuItem',
        ),
        migrations.DeleteModel(
            name='PizzaBase',
        ),
        migrations.RemoveField(
            model_name='pizzaingredientlink',
            name='menu_item',
        ),
    ]
