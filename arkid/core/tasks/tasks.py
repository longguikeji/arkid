import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arkid.settings')
django.setup()

from arkid.extension.models import TenantExtensionConfig, Extension
from arkid.core.event import Event, dispatch_event, APP_START
from arkid.core.perm.permission_data import PermissionData
from arkid.config import get_app_config
from arkid.common.logger import logger
from arkid.core.models import Tenant
from types import SimpleNamespace
from arkid.core.api import api
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
def update_app_permission(tenant_id, app_id):
    '''
    更新应用权限
    '''
    permissiondata = PermissionData()
    permissiondata.update_app_permission(tenant_id, app_id)

@app.task
def update_system_permission():
    '''
    更新系统权限
    '''
    permissiondata = PermissionData()
    permissiondata.update_system_permission()

@app.task
def update_single_user_system_permission(tenant_id, user_id):
    '''
    更新单个用户的系统权限
    '''
    permissiondata = PermissionData()
    permissiondata.update_single_user_system_permission(tenant_id, user_id)

@app.task
def update_single_user_app_permission(tenant_id, user_id, app_id):
    '''
    更新单个用户的应用权限
    '''
    permissiondata = PermissionData()
    permissiondata.update_single_user_app_permission(tenant_id, user_id, app_id)

@app.task
def add_system_permission_to_user(tenant_id, user_id, permission_id):
    '''
    添加系统权限给用户
    '''
    permissiondata = PermissionData()
    permissiondata.add_system_permission_to_user(tenant_id, user_id, permission_id)

@app.task
def remove_system_permission_to_user(tenant_id, user_id, permission_id):
    '''
    移除系统权限
    '''
    permissiondata = PermissionData()
    permissiondata.remove_system_permission_to_user(tenant_id, user_id, permission_id)

@app.task
def add_app_permission_to_user(tenant_id, app_id, user_id, permission_id):
    '''
    添加应用权限用户
    '''
    permissiondata = PermissionData()
    permissiondata.add_app_permission_to_user(tenant_id, app_id, user_id, permission_id)


@app.task
def remove_app_permission_to_user(tenant_id, app_id, user_id, permission_id):
    '''
    移除应用权限用户
    '''
    permissiondata = PermissionData()
    permissiondata.remove_app_permission_to_user(tenant_id, app_id, user_id, permission_id)

class ReadyCelery(object):

    def __init__(self, *args, **kwargs):
        pass

    @classmethod
    def instance(cls, *args, **kwargs):
        if not hasattr(ReadyCelery, "_instance"):
            ReadyCelery._instance = ReadyCelery(*args, **kwargs)
            update_system_permission.delay()
        return ReadyCelery._instance
        
ReadyCelery.instance()