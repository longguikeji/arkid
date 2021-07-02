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
    delete_group,
    patch_group)
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

    cookies = {'sessionid': 'hgnk3f0j2fmt70zc484l0ajdv7xj13q1'}
    cookies = {'sessionid': 'yhoyqw29ew439sjrh7gdktzm3pkngyc7'}
    scim_client = config.get_scim_client(cookies=cookies)
    is_exists, user_uuid = user_exists(scim_client, config, user)
    if not is_exists:
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
    if not config.should_provision_user(user):
        print(f'User deprovisioning Skiped: {user_id}')
        return

    cookies = {'sessionid': 'yhoyqw29ew439sjrh7gdktzm3pkngyc7'}
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

    cookies = {'sessionid': 'yhoyqw29ew439sjrh7gdktzm3pkngyc7'}
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

    cookies = {'sessionid': 'yhoyqw29ew439sjrh7gdktzm3pkngyc7'}
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
    '''
    同步的前提是User和Group已经同步到服务端
    '''
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

        user = User.objects.get(id=user_id)
        if not user:
            return

        if action == 'pre_clear':
            groups = user.groups.all()
            for grp in groups:
                provision_update_group_members(config.id, user.id, grp.id, 'Remove')

        elif action == 'pre_add':
            for grp_id in group_set:
                grp = Group.objects.get(id=grp_id)
                provision_update_group_members(config.id, user.id, grp.id, 'Add')

        elif action == 'pre_remove':
            for grp in group_set:
                grp = Group.objects.get(id=grp_id)
                provision_update_group_members(config.id, user.id, grp.id, 'Remove')

def get_user_group_uuid(scim_client, config, user_id, group_id):
    user: User = User.objects.get(id=user_id)
    group: Group = Group.objects.get(id=group_id)

    if not config.should_provision_user(user):
        print(f'User Provisioning Skiped: {user_id}')
        return (None, None)

    if not config.should_provision_group(group):
        print(f'Group Provisioning Skiped: {group_id}')
        return (None, None)


    _, user_uuid = user_exists(scim_client, config, user)
    _, group_uuid = group_exists(scim_client, config, group)

    return (user_uuid, group_uuid)

@app.task
def provision_update_group_members(config_id, user_id, group_id, operation):
    print(f'group:{group_id} {operation} user:{user_id}')
    config: Config = Config.objects.get(id=config_id)
    cookies = {'sessionid': 'yhoyqw29ew439sjrh7gdktzm3pkngyc7'}
    scim_client = config.get_scim_client(cookies=cookies)

    user_uuid, group_uuid = get_user_group_uuid(scim_client, config, user_id, group_id)
    if not user_uuid or not group_uuid:
        return
    data = {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
        "Operations": [{
            "op": operation,
            "path": "members",
            "value": [{
                "$ref": None,
                "value": user_uuid
            }]
        }]
    }

    ret = patch_group(scim_client, group_uuid, data)
    if ret:
        print(f'group{group_uuid} {operation} user{user_uuid} success')
    else:
        print(f'group{group_uuid} {operation} user{user_uuid} failed')
