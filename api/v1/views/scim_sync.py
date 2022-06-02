from arkid.core.api import api, operation
import json
from ninja import Schema
from ninja import ModelSchema
from arkid.core.translation import gettext_default as _
from arkid.core.extension.scim_sync import ScimSyncExtension
from arkid.extension.utils import import_extension
from arkid.extension.models import TenantExtensionConfig, Extension
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from arkid.common.logger import logger
from typing import List
from ninja.pagination import paginate
from django.shortcuts import get_object_or_404
from uuid import UUID
from arkid.core.error import ErrorCode
from arkid.core.pagenation import CustomPagination

from api.v1.schema.scim_sync import (
    ScimSyncCreateIn,
    ScimSyncCreateOut,
    ScimSyncDeleteOut,
    ScimSyncListItemOut,
    ScimSyncListOut,
    ScimSyncOut,
    ScimSyncUpdateIn,
    ScimSyncUpdateOut,
)


def update_or_create_periodic_task(extension_config):
    crontab = extension_config.config.get('crontab')
    if crontab:
        try:
            crontab = crontab.split(' ')
            crontab.extend(['*'] * (5 - len(crontab)))

            # create CrontabSchedule
            schedule, _ = CrontabSchedule.objects.get_or_create(
                minute=crontab[0],
                hour=crontab[1],
                day_of_week=crontab[2],
                day_of_month=crontab[3],
                month_of_year=crontab[4],
            )

            # create PeriodicTask
            PeriodicTask.objects.update_or_create(
                name=extension_config.id,
                defaults={
                    'crontab': schedule,
                    'task': 'arkid.core.tasks.sync',
                    'args': json.dumps([extension_config.id.hex]),
                    'kwargs': json.dumps(extension_config.config),
                },
            )
        except Exception as e:
            logger.exception('add celery task failed %s' % e)


def delete_periodic_task(extension_config):
    try:
        # fake delete triggers post_save signal
        PeriodicTask.objects.filter(name=extension_config.id).delete()
    except Exception as e:
        logger.exception('delete celery task failed %s' % e)


@api.get(
    "/tenant/{tenant_id}/scim_syncs/",
    response=List[ScimSyncListItemOut],
    tags=[_("用户数据同步配置")],
    auth=None,
)
@operation(ScimSyncListOut)
@paginate(CustomPagination)
def get_scim_syncs(request, tenant_id: str):
    """用户数据同步配置列表"""
    configs = TenantExtensionConfig.valid_objects.filter(
        tenant_id=tenant_id, extension__type="scim_sync"
    )
    return [
        {
            "id": config.id.hex,
            "type": config.type,
            "name": config.name,
            "extension_name": config.extension.name,
            "extension_package": config.extension.package,
        }
        for config in configs
    ]


@api.get(
    "/tenant/{tenant_id}/scim_syncs/{id}/",
    response=ScimSyncOut,
    tags=[_("用户数据同步配置")],
    auth=None,
)
@operation(ScimSyncOut)
def get_scim_sync(request, tenant_id: str, id: str):
    """获取用户数据同步配置"""
    config = TenantExtensionConfig.valid_objects.get(tenant__id=tenant_id, id=id)
    return {
        "data": {
            "id": config.id.hex,
            "type": config.type,
            "package": config.extension.package,
            "name": config.name,
            "config": config.config,
        }
    }


@api.post(
    "/tenant/{tenant_id}/scim_syncs/",
    tags=[_("用户数据同步配置")],
    response=ScimSyncCreateOut,
    auth=None,
)
@operation(ScimSyncCreateOut)
def create_scim_sync(request, tenant_id: str, data: ScimSyncCreateIn):
    """创建用户数据同步配置"""

    extension = Extension.valid_objects.get(package=data.package)
    extension = import_extension(extension.ext_dir)
    config = extension.create_tenant_config(
        request.tenant, data.config.dict(), name=data.dict().get("name"), type=data.type
    )
    if data.config.mode == "client":
        update_or_create_periodic_task(config)
    return {'error': ErrorCode.OK.value}


@api.put(
    "/tenant/{tenant_id}/scim_syncs/{id}/",
    tags=[_("用户数据同步配置")],
    response=ScimSyncUpdateOut,
    auth=None,
)
@operation(ScimSyncUpdateOut)
def update_scim_sync(request, tenant_id: str, id: str, data: ScimSyncUpdateIn):
    """编辑用户数据同步配置"""

    config = TenantExtensionConfig.active_objects.get(tenant__id=tenant_id, id=id)
    for attr, value in data.dict().items():
        setattr(config, attr, value)
    config.save()
    if data.config.mode == "client":
        update_or_create_periodic_task(config)

    return {'error': ErrorCode.OK.value}


@api.delete("/tenant/{tenant_id}/scim_syncs/{id}/", tags=[_("用户数据同步配置")], auth=None)
@operation(ScimSyncDeleteOut)
def delete_scim_sync(request, tenant_id: str, id: str):
    """删除用户数据同步配置"""
    config = TenantExtensionConfig.valid_objects.get(tenant__id=tenant_id, id=id)
    if config.config["mode"] == "client":
        delete_periodic_task(config)
    config.delete()
    return {'error': ErrorCode.OK.value}


class ScimServerOut(ModelSchema):
    class Config:
        model = TenantExtensionConfig
        model_fields = ['id', 'name', 'type']


@api.get(
    "/tenant/{tenant_id}/scim_server_list/",
    response=List[ScimServerOut],
    tags=['用户数据同步配置'],
    auth=None,
)
def list_scim_servers(request, tenant_id: str):
    """获取Scim同步server列表"""
    qs = TenantExtensionConfig.active_objects.filter(
        extension__type='scim_sync', config__mode='server'
    ).all()
    return qs
