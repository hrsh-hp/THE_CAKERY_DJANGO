# Generated by Django 5.1.6 on 2025-03-26 09:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cakes', '0008_order_delivery_person_alter_order_status_review'),
    ]

    operations = [
        migrations.CreateModel(
            name='CakeSponge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sponge', models.CharField(max_length=50)),
                ('price', models.DecimalField(decimal_places=2, max_digits=6)),
                ('slug', models.SlugField(blank=True, null=True, unique=True)),
                ('cake', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sponges', to='cakes.cake')),
            ],
        ),
    ]
