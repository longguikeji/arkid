# Generated by Django 3.2.13 on 2022-08-03 06:59

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='WechatscanUser',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, unique=True, verbose_name='ID')),
                ('is_del', models.BooleanField(default=False, verbose_name='是否删除')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否可用')),
                ('updated', models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建时间')),
                ('wechatscan_user_id', models.CharField(blank=True, max_length=255, verbose_name='wechatscan_user_id')),
                ('target', models.OneToOneField(blank=True, default=None, on_delete=django.db.models.deletion.PROTECT, related_name='com_longgui_external_idp_wechatscan_wechatscanuser', to='core.user')),
            ],
        ),
    ]
