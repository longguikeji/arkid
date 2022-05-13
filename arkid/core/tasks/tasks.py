import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arkid.settings')
django.setup()

from arkid.extension.models import TenantExtensionConfig, Extension
from arkid.core.models import (
  SystemPermission, UserPermissionResult, User,
  Tenant
)
from arkid.core.b64_compress import Compress
from arkid.core.openapi import get_permissions
from arkid.core.event import Event, dispatch_event, APP_START
from arkid.core.api import api
from django.db.models import Q
from arkid.config import get_app_config
from arkid.common.logger import logger
from types import SimpleNamespace
from celery import shared_task
from .celery import app
import requests, uuid
import importlib
import collections

@shared_task(bind=True)
def sync(self, config_id, *args, **kwargs):

    try:
        logger.info("=== arkid.core.tasks.sync start...===")
        logger.info(f"config_id: {config_id}")
        logger.info(f"kwargs: {kwargs}")
        extension_config = TenantExtensionConfig.active_objects.get(id=config_id)
        extension = extension_config.extension
        ext_dir = extension.ext_dir
        logger.info(f"Importing  {ext_dir}")
        ext_name = str(ext_dir).replace('/','.')
        ext = importlib.import_module(ext_name)
        if ext and hasattr(ext, 'extension'):
            ext.extension.sync(extension_config)
            logger.info("=== arkid.core.tasks.sync end...===")
        else:
            logger.error(f'{ext_name} import fail')
            return None
    except Exception as exc:
        max_retries = kwargs.get('max_retries', 3)
        countdown = kwargs.get('retry_delay', 5 * 60)
        raise self.retry(exc=exc, max_retries=max_retries, countdown=countdown)

@app.task
def update_system_permission():
    '''
    更新系统权限
    '''
    # 取得所有的系统权限
    update_arkid_system_permission()
    # 更新所有用户的系统权限
    update_arkid_all_user_permission()

@app.task
def update_single_user_system_permission(tenant_id, user_id):
    '''
    更新单个用户的系统权限
    '''
    tenant = Tenant.valid_objects.filter(id=tenant_id).first()
    user = User.valid_objects.filter(id=user_id).first()
    if tenant and user:
      update_arkid_single_user_permission(tenant, user)
    else:
      print('不存在租户或者用户无法更新')

def update_arkid_system_permission():
    '''
    更新系统权限
    '''
    permissions_data = get_permissions(api)
    group_data = []
    api_data = []
    old_permissions = SystemPermission.valid_objects.filter(
      Q(code__icontains='group_role') | Q(category='api'),
      tenant=None,
      is_system=True,
    )
    for old_permission in old_permissions:
        old_permission.is_update = False
        old_permission.save()
    for permissions_item in permissions_data:
        name = permissions_item.get('name', '')
        sort_id = permissions_item.get('sort_id', 0)
        type = permissions_item.get('type', '')
        container = permissions_item.get('container', [])
        operation_id = permissions_item.get('operation_id')
        if type == 'group':
          group_data.append(permissions_item)
          systempermission = SystemPermission.valid_objects.filter(
              tenant=None,
              category='group',
              is_system=True,
              name=name,
              code__icontains='group_role',
          ).first()
          if not systempermission:
            systempermission = SystemPermission()
            systempermission.category = 'group'
            systempermission.is_system = True
            systempermission.name = name
            systempermission.code = 'group_role_{}'.format(uuid.uuid4())
            systempermission.tenant = None
            systempermission.operation_id = ''
            systempermission.describe = {}
          systempermission.is_update = True
          systempermission.save()
        else:
          api_data.append(permissions_item)
          systempermission, is_create = SystemPermission.objects.get_or_create(
              category='api',
              is_system=True,
              is_del=False,
              operation_id=operation_id,
          )
          if is_create is True:
            systempermission.code = 'api_{}'.format(uuid.uuid4())
          systempermission.name = name
          systempermission.describe = {
          }
          systempermission.is_update = True
          systempermission.save()
        permissions_item['sort_real_id'] = systempermission.sort_id
        permissions_item['systempermission'] = systempermission
    # 单独处理分组问题
    for group_item in group_data:
        container = group_item.get('container', []) 
        group_systempermission = group_item.get('systempermission', None)
        group_sort_ids = []
        for api_item in api_data:
            sort_id = api_item.get('sort_id', 0)
            sort_real_id = api_item.get('sort_real_id', 0)
            api_systempermission = api_item.get('systempermission', None)
            
            if sort_id in container and api_systempermission:
                group_systempermission.container.add(api_systempermission)
                group_sort_ids.append(sort_real_id)
        # parent
        parent = group_item.get('parent', -1)
        describe = {'sort_ids': group_sort_ids}
        if parent != -1:
          parent_real = None
          for group_next in group_data:
            sort_id = group_next.get('sort_id', 0)
            sort_real_id = group_next.get('sort_real_id', 0)
            group_next_permission = group_next.get('systempermission', None)
            if sort_id == parent and group_next_permission:
              group_systempermission.parent = group_next_permission
              describe['parent'] = sort_real_id
              break
        else:
          group_systempermission.parent = None
        group_systempermission.describe = describe
        group_systempermission.save()
    # 权限更新
    SystemPermission.valid_objects.filter(
      Q(code__icontains='group_role') | Q(category='api'),
      tenant=None,
      is_system=True,
      is_update=False
    ).update(is_del=0)

def update_arkid_single_user_permission(tenant, auth_user):
    '''
    更新指定用户权限
    '''
    is_tenant_admin = tenant.has_admin_perm(auth_user)
    system_permissions = SystemPermission.valid_objects.order_by('sort_id')
    data_dict = {}
    for system_permission in system_permissions:
      data_dict[system_permission.sort_id] = system_permission
    # 取得当前用户权限数据
    userpermissionresult = UserPermissionResult.valid_objects.filter(
      user=auth_user,
      tenant=tenant,
      app=None,
    ).first()
    compress = Compress()
    permission_result = ''
    if userpermissionresult:
      permission_result = compress.decrypt(userpermissionresult.result)
    # 对数据进行一次排序
    data_dict = collections.OrderedDict(sorted(data_dict.items(), key=lambda obj: obj[0]))

    permission_result_arr = []
    if permission_result:
      permission_result_arr = list(permission_result)
      for data_item in data_dict.values():
        sort_id = data_item.sort_id
        sort_id_result = int(permission_result_arr[sort_id])
        if sort_id_result == 1:
          data_item.is_pass = 1
        else:
          data_item.is_pass = 0
    # 权限检查
    for data_item in data_dict.values():
      # 如果是通过就不查验
      if hasattr(data_item, 'is_pass') == True and data_item.is_pass == 1:
        continue
      # 如果是超级管理员直接就通过
      if auth_user.is_superuser:
        data_item.is_pass = 1
      else:
        if data_item.name == 'normal-user':
          data_item.is_pass = 1
          describe = data_item.describe
          container = describe.get('sort_ids')
          if container:
            for item in container:
                data_dict.get(item).is_pass = 1
        elif data_item.name == 'tenant-admin' and is_tenant_admin:
          data_item.is_pass = 1
          describe = data_item.describe
          container = describe.get('sort_ids')
          if container:
            for item in container:
                data_dict.get(item).is_pass = 1
        elif data_item.name == 'platform-admin':
          # 平台管理员默认有所有权限所有这里没必要做处理
          pass
        elif hasattr(data_item, 'is_pass') == False:
          data_item.is_pass = 0
        else:
          data_item.is_pass = 0
    # 产生结果字符串
    if permission_result:
      for data_item in data_dict.values():
        permission_result_arr[data_item.sort_id] = data_item.is_pass
    else:
      for data_item in data_dict.values():
        permission_result_arr.append(data_item.is_pass)
    permission_result = "".join(map(str, permission_result_arr))
    compress_str_result = compress.encrypt(permission_result)
    if compress_str_result:
      userpermissionresult, is_create = UserPermissionResult.objects.get_or_create(
        is_del=False,
        user=auth_user,
        tenant=tenant,
        app=None,
      )
      userpermissionresult.is_update = True
      userpermissionresult.result = compress_str_result
      userpermissionresult.save()

def update_arkid_all_user_permission():
    '''
    更新所有用户权限
    '''
    tenant, _ = Tenant.objects.get_or_create(
        slug='',
        name="platform tenant",
    )
    # 取得当前租户的所有用户
    auth_users = User.valid_objects.filter(tenant__id=tenant.id)
    # 区分出那些人是管理员
    systempermission = SystemPermission.valid_objects.filter(tenant=tenant, code=tenant.admin_perm_code, is_system=True).first()
    userpermissionresults = UserPermissionResult.valid_objects.filter(
        tenant=tenant,
        app=None,
    )
    userpermissionresults_dict = {}
    compress = Compress()
    for userpermissionresult in userpermissionresults:
      userpermissionresults_dict[userpermissionresult.user.id.hex] = userpermissionresult
    for auth_user in auth_users:
      # 权限鉴定
      if auth_user.is_superuser:
        auth_user.is_tenant_admin = True
      else:
        if auth_user.id.hex in userpermissionresults_dict:
          userpermissionresult_obj = userpermissionresults_dict.get(auth_user.id.hex)
          permission_result_arr = list(userpermissionresult_obj)
          auth_user_permission_result = compress.decrypt(userpermissionresult_obj.result)
          auth_user_permission_result_arr = list(auth_user_permission_result)
          check_result = int(permission_result_arr[systempermission.sort_id])
          if check_result == 1:
            auth_user.is_tenant_admin = True
          else:
            auth_user.is_tenant_admin = False
        else:
          auth_user.is_tenant_admin = False
    # 权限数据
    system_permissions = SystemPermission.valid_objects.order_by('sort_id')
    data_dict = {}
    for system_permission in system_permissions:
      data_dict[system_permission.sort_id] = system_permission
    data_dict = collections.OrderedDict(sorted(data_dict.items(), key=lambda obj: obj[0]))
    # 计算每一个用户的权限情况
    for auth_user in auth_users:
      permission_result = ''
      permission_result_arr = []
      if auth_user.id.hex in userpermissionresults_dict:
        # 解析权限字符串
        userpermissionresult_obj = userpermissionresults_dict.get(auth_user.id.hex)
        permission_result = compress.decrypt(userpermissionresult_obj.result)
        if permission_result:
          permission_result_arr = list(permission_result)
          for data_item in data_dict.values():
            sort_id = data_item.sort_id
            sort_id_result = int(permission_result_arr[sort_id])
            if sort_id_result == 1:
              data_item.is_pass = 1
            else:
              data_item.is_pass = 0
      else:
        for data_item in data_dict.values():
          data_item.is_pass = 0
      # 权限查验
      for data_item in data_dict.values():
        # 如果是通过就不查验
        if hasattr(data_item, 'is_pass') == True and data_item.is_pass == 1:
          continue
        # 如果是超级管理员直接就通过
        if auth_user.is_superuser:
          data_item.is_pass = 1
        else:
          if data_item.name == 'normal-user':
            data_item.is_pass = 1
            describe = data_item.describe
            container = describe.get('sort_ids')
            if container:
              for item in container:
                  data_dict.get(item).is_pass = 1
          elif data_item.name == 'tenant-admin' and auth_user.is_tenant_admin:
            data_item.is_pass = 1
            describe = data_item.describe
            container = describe.get('sort_ids')
            if container:
              for item in container:
                  data_dict.get(item).is_pass = 1
          elif data_item.name == 'platform-admin':
            # 平台管理员默认有所有权限所有这里没必要做处理
            pass
          elif hasattr(data_item, 'is_pass') == False:
            data_item.is_pass = 0
          else:
            data_item.is_pass = 0
      # 产生结果字符串
      if permission_result:
        for data_item in data_dict.values():
          permission_result_arr[data_item.sort_id] = data_item.is_pass
      else:
        for data_item in data_dict.values():
          permission_result_arr.append(data_item.is_pass)
      permission_result = "".join(map(str, permission_result_arr))
      compress_str_result = compress.encrypt(permission_result)
      if compress_str_result:
        userpermissionresult, is_create = UserPermissionResult.objects.get_or_create(
          is_del=False,
          user=auth_user,
          tenant=tenant,
          app=None,
        )
        userpermissionresult.is_update = True
        userpermissionresult.result = compress_str_result
        userpermissionresult.save()


class ReadyCelery(object):

    def __init__(self):
      tenant, _ = Tenant.objects.get_or_create(
          slug='',
          name="platform tenant",
      )
      dispatch_event(Event(tag=APP_START, tenant=tenant))

ReadyCelery()