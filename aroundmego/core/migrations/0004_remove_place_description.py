# Generated by Django 5.1.1 on 2024-10-14 01:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_placedescription'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='place',
            name='description',
        ),
    ]
