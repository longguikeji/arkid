from arkid.core.api import api, operation
from arkid.core.translation import gettext_default as _
from arkid.extension.models import TenantExtensionConfig, Extension
from arkid.extension.utils import import_extension
from django.shortcuts import get_object_or_404
from arkid.core.error import ErrorCode
from ninja import ModelSchema
from typing import List
import json
from ninja.pagination import paginate
from arkid.core.event import (
    dispatch_event,
    Event,
    CREATE_ACCOUNT_LIFE_CONFIG,
    UPDATE_ACCOUNT_LIFE_CONFIG,
    DELETE_ACCOUNT_LIFE_CONFIG,
)
from api.v1.schema.account_life import (
    AccountLifeCreateIn,
    AccountLifeCreateOut,
    AccountLifeDeleteOut,
    AccountLifeListItemOut,
    AccountLifeListOut,
    AccountLifeOut,
    AccountLifeUpdateIn,
    AccountLifeUpdateOut,
    AccountLifeCrontabOut,
    AccountLifeCrontabSchema,
)
from arkid.core.pagenation import CustomPagination
from arkid.core.extension.account_life import AccountLifeExtension
from arkid.core.models import AccountLifeCrontab
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from arkid.common.logger import logger


@api.get(
    "/tenant/{tenant_id}/account_lifes/",
    tags=["账号生命周期"],
    auth=None,
    response=List[AccountLifeListItemOut],
)
@operation(AccountLifeListOut)
@paginate(CustomPagination)
def get_account_life_list(request, tenant_id: str):
    """账号生命周期配置列表"""
    configs = TenantExtensionConfig.valid_objects.filter(
        tenant_id=tenant_id, extension__type=AccountLifeExtension.TYPE
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
    "/tenant/{tenant_id}/account_lifes/{id}/",
    tags=["账号生命周期"],
    auth=None,
    response=AccountLifeOut,
)
@operation(AccountLifeOut)
def get_account_life(request, tenant_id: str, id: str):
    """获取账号生命周期配置"""
    config = TenantExtensionConfig.active_objects.get(id=id)
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
    "/tenant/{tenant_id}/account_lifes/",
    tags=["账号生命周期"],
    auth=None,
    response=AccountLifeCreateOut,
)
@operation(AccountLifeCreateOut)
def create_account_life(request, tenant_id: str, data: AccountLifeCreateIn):
    """创建账号生命周期配置"""
    extension = Extension.valid_objects.get(package=data.package)
    extension = import_extension(extension.ext_dir)
    config = extension.create_tenant_config(
        request.tenant, data.config.dict(), data.dict()["name"], data.type
    )
    dispatch_event(
        Event(
            tag=CREATE_ACCOUNT_LIFE_CONFIG,
            tenant=request.tenant,
            request=request,
            data=config,
        )
    )
    return {'error': ErrorCode.OK.value}


@api.put(
    "/tenant/{tenant_id}/account_lifes/{id}/",
    tags=["账号生命周期"],
    auth=None,
    response=AccountLifeUpdateOut,
)
@operation(AccountLifeUpdateOut)
def update_account_life(request, tenant_id: str, id: str, data: AccountLifeUpdateIn):
    """编辑账号生命周期配置"""
    config = TenantExtensionConfig.active_objects.get(tenant__id=tenant_id, id=id)
    for attr, value in data.dict().items():
        setattr(config, attr, value)
    config.save()
    dispatch_event(
        Event(
            tag=UPDATE_ACCOUNT_LIFE_CONFIG,
            tenant=request.tenant,
            request=request,
            data=config,
        )
    )
    return {'error': ErrorCode.OK.value}


@api.delete(
    "/tenant/{tenant_id}/account_lifes/{id}/",
    tags=["账号生命周期"],
    auth=None,
    response=AccountLifeDeleteOut,
)
@operation(AccountLifeDeleteOut)
def delete_account_life(request, tenant_id: str, id: str):
    """删除账号生命周期配置"""
    config = TenantExtensionConfig.active_objects.get(tenant__id=tenant_id, id=id)
    dispatch_event(
        Event(
            tag=DELETE_ACCOUNT_LIFE_CONFIG,
            tenant=request.tenant,
            request=request,
            data=config,
        )
    )
    config.delete()
    return {'error': ErrorCode.OK.value}


@api.get(
    "/tenant/{tenant_id}/account_life_crontab/",
    tags=["账号生命周期"],
    auth=None,
    response=AccountLifeCrontabOut,
)
@operation(AccountLifeCrontabOut)
def get_account_life_crontab(request, tenant_id: str):
    """获取账号生命周期定时任务配置"""
    crontab = AccountLifeCrontab.valid_objects.filter(tenant=request.tenant).first()
    if not crontab:
        return {"data": {"crontab": '', 'max_retries': 0, 'retry_delay': 0}}
    else:
        return {"data": crontab.config}


@api.put(
    "/tenant/{tenant_id}/account_life_crontab/",
    tags=["账号生命周期"],
    auth=None,
    response=AccountLifeCrontabOut,
)
@operation(AccountLifeCrontabOut)
def update_account_life_crontab(
    request, tenant_id: str, data: AccountLifeCrontabSchema
):
    """更新账号生命周期定时任务配置"""
    crontab = AccountLifeCrontab.valid_objects.filter(tenant=request.tenant).first()
    if not crontab:
        crontab = AccountLifeCrontab.valid_objects.create(
            tenant=request.tenant, config=data.dict()
        )
    else:
        crontab.config = data.dict()
        crontab.save()
    update_or_create_periodic_task(crontab)
    return {"data": crontab.config}


def update_or_create_periodic_task(account_life_crontab):
    crontab = account_life_crontab.config.get('crontab')
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
                name=account_life_crontab.id,
                defaults={
                    'crontab': schedule,
                    'task': 'arkid.core.tasks.account_life_periodic_task',
                    'args': json.dumps([account_life_crontab.id.hex]),
                    'kwargs': json.dumps(account_life_crontab.config),
                },
            )
        except Exception as e:
            logger.exception('Add account life celery task failed %s' % e)
        else:
            logger.info('Add account life celery task success!')
