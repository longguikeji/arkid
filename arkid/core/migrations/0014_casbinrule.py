# Generated by Django 3.2.13 on 2022-06-08 08:57

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_merge_20220602_0918'),
    ]

    operations = [
        migrations.CreateModel(
            name='CasBinRule',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, unique=True, verbose_name='ID')),
                ('is_del', models.BooleanField(default=False, verbose_name='是否删除')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否可用')),
                ('updated', models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建时间')),
                ('ptype', models.CharField(max_length=255, null=True)),
                ('v0', models.CharField(max_length=255, null=True)),
                ('v1', models.CharField(max_length=255, null=True)),
                ('v2', models.CharField(max_length=255, null=True)),
                ('v3', models.CharField(max_length=255, null=True)),
                ('v4', models.CharField(max_length=255, null=True)),
                ('v5', models.CharField(max_length=255, null=True)),
            ],
            options={
                'verbose_name': 'CasBinRule',
                'verbose_name_plural': 'CasBinRule',
            },
        ),
    ]