# Generated by Django 5.1 on 2024-11-16 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0013_booking_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='labour',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
