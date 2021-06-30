from common.event import Event
import typing
from .celery import app
from app.models import App
from django.db.models import QuerySet
from provisioning.models import Config
from provisioning.constants import ProvisioningStatus
from provisioning.utils import (
    create_user,
    user_exists,
    update_user,
    delete_user,
    group_exists,
    create_group,
    update_group,
    delete_group)
from inventory.models import User, Group
from app.models import App
from webhook.models import WebHook, WebHookTriggerHistory
import requests
from scim2_client.scim_service import ScimService
from provisioning.constants import ProvisioningType


@app.task
def provision_user(tenant_uuid: str, user_id: int, is_del: bool=False):
    apps = App.active_objects.filter(
        tenant__uuid=tenant_uuid,
    )

    for app in apps:
        config: Config = Config.active_objects.filter(
            app=app,
        ).first()

        if config is None or config.status != ProvisioningStatus.Enabled.value:
            continue
        # 只支持下游同步
        if config.sync_type == ProvisioningType.upstream.value:
            continue

        # provision_app_user.delay(tenant_uuid, app.id, config.id, user_id)
        if is_del:
            deprovision_app_user(tenant_uuid, app.id, config.id, user_id)
        else:
            provision_app_user(tenant_uuid, app.id, config.id, user_id)



@app.task
def provision_app_user(tenant_uuid: str, app_id: int, config_id: int, user_id: int):
    """
    同步逻辑：
    根据profile mapping的match attributes判断APP有没有该User,如果不存在,
    直接Create, 如果存在, 更新该User的属性

    """
    print(
        f'task: provision_app_user, tenant: {tenant_uuid}, app: {app_id}, user: {user_id}'
    )

    # TODO: check the scope of the selected range
    user: User = User.objects.get(id=user_id)
    config: Config = Config.objects.get(id=config_id)
    if not config.should_provision_user(user):
        print(f'User Provisioning Skiped: {user_id}')
        return

    cookies = {'sessionid': 'bkv1n1n0s47mbtmxgib6ssgzbfvvoj8i'}
    scim_client = config.get_scim_client(cookies=cookies)
    is_exists, user_uuid = user_exists(scim_client, config, user)
    if not user_exists:
        ret = create_user(scim_client, config, user)
        print('created user from scim server: {}'.format(ret))
    else:
        update_user(scim_client, config, user, user_uuid)


@app.task
def deprovision_app_user(tenant_uuid: str, app_id: int, config_id: int, user_id: int):
    """
    同步逻辑：
    根据profile mapping的match attributes判断APP有没有该User,如果不存在,
    直接Create, 如果存在, 更新该User的属性

    """
    print(
        f'task: provision_app_user, tenant: {tenant_uuid}, app: {app_id}, user: {user_id}'
    )

    # TODO: check the scope of the selected range
    user: User = User.objects.get(id=user_id)
    config: Config = Config.objects.get(id=config_id)
    if not config.should_provision(user):
        print(f'User deprovisioning Skiped: {user_id}')
        return

    cookies = {'sessionid': 'bkv1n1n0s47mbtmxgib6ssgzbfvvoj8i'}
    scim_client = config.get_scim_client(cookies=cookies)
    is_exists, user_uuid = user_exists(scim_client, config, user)
    if not is_exists:
        print(f'User{user_id} not found in app{app_id}, delete request skipped')
        return
    else:
        delete_user(scim_client, config, user_uuid)

@app.task
def provision_group(tenant_uuid: str, group_id: int, is_del: bool=False):
    apps = App.active_objects.filter(
        tenant__uuid=tenant_uuid,
    )

    for app in apps:
        config: Config = Config.active_objects.filter(
            app=app,
        ).first()

        if config is None or config.status != ProvisioningStatus.Enabled.value:
            continue
        # 只支持下游同步
        if config.sync_type == ProvisioningType.upstream.value:
            continue

        # provision_app_user.delay(tenant_uuid, app.id, config.id, user_id)
        if is_del:
            deprovision_app_group(tenant_uuid, app.id, config.id, group_id)
        else:
            provision_app_group(tenant_uuid, app.id, config.id, group_id)



@app.task
def provision_app_group(tenant_uuid: str, app_id: int, config_id: int, group_id: int):
    """
    同步逻辑：
    根据profile mapping的match attributes判断APP有没有该User,如果不存在,
    直接Create, 如果存在, 更新该User的属性

    """
    print(
        f'task: provision_app_group, tenant: {tenant_uuid}, app: {app_id}, group: {group_id}'
    )

    # TODO: check the scope of the selected range
    group: Group = Group.objects.get(id=group_id)
    config: Config = Config.objects.get(id=config_id)
    if not config.should_provision_group(group):
        print(f'Group Deprovisioning Skiped: {group_id}')
        return

    cookies = {'sessionid': 'bkv1n1n0s47mbtmxgib6ssgzbfvvoj8i'}
    scim_client = config.get_scim_client(cookies=cookies)
    is_exists, group_uuid = group_exists(scim_client, config, group)
    if not is_exists:
        ret = create_group(scim_client, config, group)
        print('created group from scim server: {}'.format(ret))
    else:
        update_group(scim_client, config, group, group_uuid)

@app.task
def deprovision_app_group(tenant_uuid: str, app_id: int, config_id: int, group_id: int):
    """
    同步逻辑：
    根据profile mapping的match attributes判断APP有没有该User,如果不存在,
    直接Create, 如果存在, 更新该User的属性

    """
    print(
        f'task: deprovision_app_group, tenant: {tenant_uuid}, app: {app_id}, group: {group_id}'
    )

    # TODO: check the scope of the selected range
    group: Group = Group.objects.get(id=group_id)
    config: Config = Config.objects.get(id=config_id)
    if not config.should_provision_group(group):
        print(f'Group Provisioning Skiped: {group_id}')
        return

    cookies = {'sessionid': 'bkv1n1n0s47mbtmxgib6ssgzbfvvoj8i'}
    scim_client = config.get_scim_client(cookies=cookies)
    is_exists, group_uuid = group_exists(scim_client, config, group)
    if not is_exists:
        print(f'User{group_id} not found in app{app_id}, delete request skipped')
        return
    else:
        delete_group(scim_client, config, group_uuid)

@app.task
def notify_webhook(tenant_uuid: int, event: Event):
    webhooks = WebHook.objects.filter(
        tenant__uuid=tenant_uuid,
    )

    webhook: WebHook
    for webhook in webhooks:
        r = requests.post(webhook.url)
        print(r.json())

@app.task
def provision_tenant_app(tenant_uuid: str, app_id:int):
    pass

@app.task
def provision_user_groups_changed(tenant_uuid: str, action: str, user_id: int, group_set: set):
    print(
        f'task: deprovision_app_group, tenant: {tenant_uuid}, action: {action}, group_set: {group_set}'
    )
