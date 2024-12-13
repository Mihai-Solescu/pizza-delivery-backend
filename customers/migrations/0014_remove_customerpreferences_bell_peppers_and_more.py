# Generated by Django 5.1.1 on 2024-10-13 08:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0013_remove_customerpreferences_cheese_preference_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customerpreferences',
            name='bell_peppers',
        ),
        migrations.AddField(
            model_name='customerpreferences',
            name='cheese',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='customerpreferences',
            name='mozzarella',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='customerpreferences',
            name='parmesan',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='customerpreferences',
            name='tomato_sauce',
            field=models.IntegerField(default=0),
        ),
    ]