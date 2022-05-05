# uncompyle6 version 3.8.0
# Python bytecode 3.8.0 (3413)
# Decompiled from: Python 3.8.2 (v3.8.2:7b3ab5921f, Feb 24 2020, 17:52:18) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: /Users/attackt/Desktop/arkid/arkid/core/migrations/0003_alter_permission_tenant_apipermission.py
# Compiled at: 2022-04-25 17:39:13
# Size of source mod 2**32: 2751 bytes
from django.db import migrations, models
import django.db.models.deletion, uuid

class Migration(migrations.Migration):
    dependencies = [
     ('core', '0002_initial')]
    operations = [
     migrations.AlterField(model_name='permission',
       name='tenant',
       field=models.ForeignKey(blank=True, default=None, null=True, on_delete=(django.db.models.deletion.PROTECT), to='core.tenant', verbose_name='Tenant')),
     migrations.CreateModel(name='ApiPermission',
       fields=[
      (
       'id', models.UUIDField(default=(uuid.uuid4), primary_key=True, serialize=False, unique=True, verbose_name='UUID')),
      (
       'is_del', models.BooleanField(default=False, verbose_name='是否删除')),
      (
       'is_active', models.BooleanField(default=True, verbose_name='是否可用')),
      (
       'updated', models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')),
      (
       'created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建时间')),
      (
       'name', models.CharField(max_length=255, verbose_name='Name')),
      (
       'code', models.CharField(max_length=100, verbose_name='Code')),
      (
       'category', models.CharField(choices=[('entry', 'entry'), ('api', 'API'), ('data', 'data'), ('group', 'group'), ('ui', 'UI'), ('other', 'other')], default='other', max_length=100, verbose_name='category')),
      (
       'is_system', models.BooleanField(default=True, verbose_name='System Permission')),
      (
       'operation_id', models.CharField(blank=True, default='', max_length=256, null=True, verbose_name='操作id')),
      (
       'request_url', models.CharField(blank=True, default='', max_length=256, null=True, verbose_name='请求地址')),
      (
       'request_type', models.CharField(blank=True, default='', max_length=256, null=True, verbose_name='请求方法')),
      (
       'is_update', models.BooleanField(default=False, verbose_name='是否更新')),
      (
       'base_code', models.CharField(blank=True, default='', max_length=256, null=True, verbose_name='应用code')),
      (
       'app', models.ForeignKey(blank=True, default=None, null=True, on_delete=(django.db.models.deletion.PROTECT), to='core.app', verbose_name='APP')),
      (
       'tenant', models.ForeignKey(blank=True, default=None, null=True, on_delete=(django.db.models.deletion.PROTECT), to='core.tenant', verbose_name='Tenant'))],
       options={'verbose_name':'ApiPermission', 
      'verbose_name_plural':'ApiPermission'})]