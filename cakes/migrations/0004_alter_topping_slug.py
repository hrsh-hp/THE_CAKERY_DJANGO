# Generated by Django 5.1.6 on 2025-03-06 12:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cakes', '0003_topping_cake_toppings_cartitems_toppings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topping',
            name='slug',
            field=models.SlugField(blank=True, null=True, unique=True),
        ),
    ]
