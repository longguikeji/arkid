# Generated by Django 4.0.6 on 2022-11-22 07:25

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0035_privateapp_values_data'),
    ]

    operations = [
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, unique=True, verbose_name='ID')),
                ('is_del', models.BooleanField(default=False, verbose_name='是否删除')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否可用')),
                ('updated', models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建时间')),
                ('ip', models.CharField(max_length=15, unique=True, verbose_name='IP')),
            ],
            options={
                'verbose_name': 'ArkID Node',
                'verbose_name_plural': 'ArkID Node',
            },
        ),
    ]
