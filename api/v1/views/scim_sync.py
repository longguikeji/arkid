from arkid.core.api import api
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


class ScimSyncListSchemaOut(ModelSchema):
    class Config:
        model = TenantExtensionConfig
        model_fields = ['id', 'name', 'type', 'config']

    mode: str

    @staticmethod
    def resolve_mode(obj):
        return obj.config.get("mode")


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


ScimSyncConfigSchemaIn = ScimSyncExtension.create_composite_config_schema(
    'ScimSyncConfigSchemaIn'
)


class ScimSyncConfigSchemaOut(Schema):
    id: UUID
    type: str
    name: str
    config: dict


@api.get(
    "/tenant/{tenant_id}/scim_syncs/",
    response=List[ScimSyncListSchemaOut],
    tags=[_("用户数据同步配置")],
    auth=None,
)
@paginate
def get_scim_syncs(request, tenant_id: str):
    """用户数据同步配置列表,TODO"""
    configs = TenantExtensionConfig.valid_objects.filter(
        tenant_id=tenant_id, extension__type="scim_sync"
    )
    return configs


@api.get(
    "/tenant/{tenant_id}/scim_syncs/{id}/",
    response=ScimSyncConfigSchemaOut,
    tags=[_("用户数据同步配置")],
    auth=None,
)
def get_scim_sync(request, tenant_id: str, id: str):
    """获取用户数据同步配置,TODO"""
    config = get_object_or_404(TenantExtensionConfig, id=id, tenant=request.tenant)
    return config


@api.post(
    "/tenant/{tenant_id}/scim_syncs/",
    tags=[_("用户数据同步配置")],
    response=ScimSyncConfigSchemaOut,
    auth=None,
)
def create_scim_sync(request, tenant_id: str, data: ScimSyncConfigSchemaIn):
    """创建用户数据同步配置,TODO"""

    tenant = request.tenant
    package = data.package
    name = data.name
    type = data.type
    config = data.config
    extension = Extension.active_objects.get(package=package)
    extension = import_extension(extension.ext_dir)
    extension_config = extension.create_tenant_config(
        tenant, config.dict(), name=name, type=type
    )
    if config.mode == "client":
        update_or_create_periodic_task(extension_config)
    return extension_config


@api.put(
    "/tenant/{tenant_id}/scim_syncs/{id}/",
    tags=[_("用户数据同步配置")],
    response=ScimSyncConfigSchemaOut,
    auth=None,
)
def update_scim_sync(request, tenant_id: str, id: str, data: ScimSyncConfigSchemaIn):
    """编辑用户数据同步配置,TODO"""
    extension_config = get_object_or_404(
        TenantExtensionConfig, id=id, tenant=request.tenant
    )
    extension_config.package = data.package
    extension_config.name = data.name
    extension_config.type = data.type
    extension_config.config = data.config

    if data.config.mode == "client":
        update_or_create_periodic_task(extension_config)

    return extension_config


@api.delete("/tenant/{tenant_id}/scim_syncs/{id}/", tags=[_("用户数据同步配置")], auth=None)
def delete_scim_sync(request, tenant_id: str, id: str):
    """删除用户数据同步配置,TODO"""
    extension_config = get_object_or_404(
        TenantExtensionConfig, id=id, tenant=request.tenant
    )
    extension_config.delete()
    if extension_config.config["mode"] == "client":
        delete_periodic_task(extension_config)
    return {'error': ErrorCode.OK.value}
