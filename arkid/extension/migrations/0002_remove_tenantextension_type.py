# Generated by Django 3.2.13 on 2022-05-23 03:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('extension', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tenantextension',
            name='type',
        ),
    ]
