# Generated by Django 3.2.13 on 2022-10-13 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('com_longgui_default_desktop', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='defaultdesktop',
            name='default_desktop',
            field=models.CharField(blank=True, default='/desktop/', max_length=1024, null=True, verbose_name='Default Desktop'),
        ),
    ]
