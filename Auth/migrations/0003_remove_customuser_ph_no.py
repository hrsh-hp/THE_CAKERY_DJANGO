# Generated by Django 5.1.6 on 2025-03-03 18:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Auth', '0002_remove_customuser_name_customuser_user_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='ph_no',
        ),
    ]
