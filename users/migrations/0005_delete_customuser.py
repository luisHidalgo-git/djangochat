# Generated by Django 5.1.2 on 2025-03-08 04:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20250308_0406'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CustomUser',
        ),
    ]
