# Generated by Django 3.2.13 on 2022-06-01 06:39

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0011_auto_20220601_0636'),
    ]

    operations = [
        migrations.CreateModel(
            name='CaseUser',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, unique=True, verbose_name='ID')),
                ('is_del', models.BooleanField(default=False, verbose_name='是否删除')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否可用')),
                ('updated', models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建时间')),
                ('nickname', models.CharField(max_length=128, verbose_name='Nickname')),
                ('target', models.ForeignKey(blank=True, default=None, on_delete=django.db.models.deletion.PROTECT, related_name='com_longgui_case_caseuser', to='core.user')),
            ],
        ),
    ]
