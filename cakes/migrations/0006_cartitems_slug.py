# Generated by Django 5.1.6 on 2025-03-06 20:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cakes', '0005_alter_cartitems_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitems',
            name='slug',
            field=models.SlugField(blank=True, null=True, unique=True),
        ),
    ]
