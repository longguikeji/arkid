# Generated by Django 3.2.13 on 2022-05-20 04:54

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Extension',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, unique=True, verbose_name='ID')),
                ('is_del', models.BooleanField(default=False, verbose_name='是否删除')),
                ('updated', models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建时间')),
                ('type', models.CharField(default='base', max_length=64, verbose_name='类型')),
                ('labels', models.CharField(max_length=128, verbose_name='标签')),
                ('package', models.CharField(db_index=True, max_length=128, unique=True, verbose_name='标识')),
                ('ext_dir', models.CharField(max_length=1024, verbose_name='完整路径名')),
                ('name', models.CharField(max_length=128, verbose_name='名称')),
                ('version', models.CharField(max_length=128, verbose_name='版本')),
                ('is_active', models.BooleanField(default=False, verbose_name='是否启动')),
                ('profile', models.JSONField(blank=True, default=dict, verbose_name='Setup Profile')),
                ('is_allow_use_platform_config', models.BooleanField(default=False, verbose_name='是否允许租户使用平台配置')),
            ],
            options={
                'verbose_name': '插件',
                'verbose_name_plural': '插件',
            },
        ),
        migrations.CreateModel(
            name='TenantExtensionConfig',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, unique=True, verbose_name='ID')),
                ('is_del', models.BooleanField(default=False, verbose_name='是否删除')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否可用')),
                ('updated', models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建时间')),
                ('config', models.JSONField(blank=True, default=dict, verbose_name='Runtime Config')),
                ('name', models.CharField(default='', max_length=128, verbose_name='名称')),
                ('type', models.CharField(default='', max_length=128, verbose_name='类型')),
                ('extension', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='extension.extension', verbose_name='插件')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.tenant', verbose_name='租户')),
            ],
            options={
                'verbose_name': '插件运行时配置',
                'verbose_name_plural': '插件运行时配置',
            },
        ),
        migrations.CreateModel(
            name='TenantExtension',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, unique=True, verbose_name='ID')),
                ('is_del', models.BooleanField(default=False, verbose_name='是否删除')),
                ('updated', models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建时间')),
                ('settings', models.JSONField(blank=True, default=dict, verbose_name='Tenant Settings')),
                ('is_active', models.BooleanField(default=False, verbose_name='是否使用')),
                ('use_platform_config', models.BooleanField(default=False, verbose_name='是否使用平台配置')),
                ('type', models.CharField(default='', max_length=128, verbose_name='类型')),
                ('extension', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='extension.extension', verbose_name='插件')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.tenant', verbose_name='租户')),
            ],
            options={
                'verbose_name': '插件租户配置',
                'verbose_name_plural': '插件租户配置',
                'unique_together': {('tenant', 'extension')},
            },
        ),
    ]
