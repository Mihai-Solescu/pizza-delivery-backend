# Generated by Django 5.1.1 on 2024-10-14 18:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('delivery', '0004_rename_delivery_address_delivery_delivery_postal_code_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='delivery',
            old_name='delivery_person_id',
            new_name='delivery_person',
        ),
        migrations.AddField(
            model_name='delivery',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True, blank=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='delivery',
            name='delivery_address',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='delivery',
            name='delivery_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('in_process', 'In Process'), ('completed', 'Completed'), ('no_courier', 'No Courier')], default='pending', max_length=20),
        ),
    ]