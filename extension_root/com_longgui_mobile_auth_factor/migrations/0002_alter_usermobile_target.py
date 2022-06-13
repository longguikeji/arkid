# Generated by Django 3.2.13 on 2022-06-09 10:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_merge_20220602_0918'),
        ('com_longgui_mobile_auth_factor', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usermobile',
            name='target',
            field=models.OneToOneField(blank=True, default=None, on_delete=django.db.models.deletion.PROTECT, related_name='com_longgui_mobile_auth_factor_usermobile', to='core.user'),
        ),
    ]