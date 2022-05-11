import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arkid.settings')
django.setup()

from arkid.extension.models import TenantExtensionConfig, Extension
from arkid.core.models import SystemPermission
from arkid.core.openapi import get_permissions
from arkid.core.event import Event, dispatch_event, APP_START
from arkid.core.models import Tenant
from arkid.core.api import api
from django.db.models import Q
from arkid.config import get_app_config
from arkid.common.logger import logger
from types import SimpleNamespace
from celery import shared_task
from .celery import app
import requests, uuid
import importlib

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
    ).delete()

class ReadySingleton(object):
    def __init__(self, *args, **kwargs):
        pass
        
    @classmethod
    def get_instance(cls, *args, **kwargs): 
        if not hasattr(ReadySingleton, '_instance' ):
            ReadySingleton._instance = ReadySingleton(*args, **kwargs)
            # 只有celery第一次被启动时才会调用
            tenant = Tenant.valid_objects.filter(
                slug='',
                name="platform tenant",
            ).first()
            dispatch_event(Event(tag=APP_START, tenant=tenant))
        return ReadySingleton._instance

ReadySingleton.get_instance()