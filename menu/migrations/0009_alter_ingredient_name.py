# Generated by Django 5.1.1 on 2024-10-15 03:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0008_ingredientfilters'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(max_length=30, unique=True),
        ),
    ]
