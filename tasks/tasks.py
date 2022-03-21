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
    patch_group,
)
from inventory.models import User, Group
from app.models import App
from config import get_app_config
from inventory.models import Permission, PermissionGroup

# from webhook.models import WebHook, WebHookTriggerHistory
from common.utils import send_email as send_email_func
import requests
from provisioning.constants import ProvisioningType

import requests
import json
import uuid


@app.task
def provision_user(tenant_uuid: str, user_id: int, is_del: bool = False):
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
def provision_group(tenant_uuid: str, group_id: int, is_del: bool = False):
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


# @app.task
# def notify_webhook(tenant_uuid: int, event: Event):
#     webhooks = WebHook.objects.filter(
#         tenant__uuid=tenant_uuid,
#     )

#     webhook: WebHook
#     for webhook in webhooks:
#         r = requests.post(webhook.url)
#         print(r.json())


@app.task
def send_email(addrs, subject, content):
    '''
    发送邮件
    '''
    send_email_func(addrs, subject, content)


@app.task
def update_permission():
    '''
    定时更新权限
    '''
    c = get_app_config()
    api_info = "{}/api/schema/?format=json".format(c.get_host())
    response = requests.get(api_info)
    response = response.json()
    # 权限分组更新
    info = response.get('info')
    roles_describe = info.get('roles_describe')
    base_code = roles_describe.get('code')
    roles = {

    }
    # 权限更新
    paths = response.get('paths')
    path_keys = paths.keys()
    # 所有权限数据重置为没更新
    old_permissions = Permission.valid_objects.filter(
        tenant=None,
        app=None,
        content_type=None,
        permission_category='API',
        is_system_permission=True,
        base_code=base_code,
    )
    for old_permission in old_permissions:
        old_permission.is_update = False
        old_permission.save()
    for path_key in path_keys:
        item = paths.get(path_key)
        item_keys = item.keys()
        for item_key in item_keys:
            request_obj = item.get(item_key)
            # 参数信息
            request_type = item_key
            request_url = path_key
            action = request_obj.get('action')
            summary = request_obj.get('summary', '')
            description = request_obj.get('description')
            operation_id = request_obj.get('operationId')
            # 缓存数据
            # content_type = ContentType.objects.get_for_model(Tenant)
            codename = 'api_{}'.format(uuid.uuid4())
            permission, is_create = Permission.objects.get_or_create(
                is_del=False,
                operation_id=operation_id
            )
            if is_create is True:
                permission.codename = codename
            permission.name = summary
            permission.content_type = None
            permission.tenant = None
            permission.app = None
            permission.is_update = True
            permission.permission_category = 'API'
            permission.is_system_permission = True
            permission.action = action
            permission.base_code = base_code
            permission.description = description
            permission.request_url = request_url
            permission.request_type = request_type
            permission.save()
            # 统计所有的角色
            roles_obj = request_obj.get('roles', [])
            for role in roles_obj:
                role_list = []
                if role in roles:
                    role_list = roles[role]
                role_list.append(permission)
                roles[role] = role_list
    # 删掉没更新的数据
    Permission.valid_objects.filter(
        tenant=None,
        app=None,
        content_type=None,
        permission_category='API',
        is_system_permission=True,
        base_code=base_code,
        is_update=False,
    ).delete()
    # 权限分组
    base_title = roles_describe.get('name', '')
    base_children = roles_describe.get('children', [])
    roles_describe = {}
    # 处理子对象
    process_child(roles_describe, base_children, '')
    base_permission_group, is_create = PermissionGroup.objects.get_or_create(
        is_active=True,
        is_del=False,
        name=base_title,
        en_name=base_code,
        title=base_title,
        base_code=base_code,
        is_system_group=True,
        is_update=True,
    )
    # 将权限分组的更新状态统统重置为false
    old_permissiongroups = PermissionGroup.valid_objects.filter(
        title=base_title,
        tenant=None,
        is_system_group=True,
        base_code=base_code,
        is_update=True,
    ).exclude(uuid=base_permission_group.uuid)
    for old_permissiongroup in old_permissiongroups:
        old_permissiongroup.is_update = False
        old_permissiongroup.save()
    # 权限分组实体
    for role_key in roles.keys():
        # 先要看看有几级
        role_key_arr = role_key.split('.')
        role_key_temp_arr=[]
        parent_list = []
        for index, role_key_item in enumerate(role_key_arr):
            # 先加进数组
            role_key_temp_arr.append(role_key_item)
            # 在拼接
            role_key_item = '.'.join(role_key_temp_arr)    
            permissiongroup, is_create = PermissionGroup.objects.get_or_create(
                is_del=False,
                tenant=None,
                en_name=role_key_item,
                is_system_group=True,
                base_code=base_code,
                title=base_title,
            )
            permissiongroup.name = roles_describe.get(role_key_item, '')
            permissiongroup.is_update = True
            if index == 0:
                # 第一项没父亲(arkid)
                permissiongroup.parent = base_permission_group
            else:
                # 前一项设置为父亲
                permissiongroup.parent = parent_list[index-1]
            permissiongroup.save()
            # 清理掉权限
            permissiongroup.permissions.clear()
            # 额外添加
            parent_list.append(permissiongroup)
            # 给匹配权限
            for role in roles.get(role_key_item, []):
                permissiongroup.permissions.add(role)
    # 删掉没更新的数据
    PermissionGroup.valid_objects.filter(
        tenant=None,
        is_system_group=True,
        is_update=False,
        title=base_title,
        base_code=base_code,
    ).exclude(uuid=base_permission_group.uuid).delete()

def process_child(roles_describe, base_children, base_code):
    '''
    处理子对象
    '''
    base_temp_code = base_code
    for item in base_children:
        # 处理code
        code = item.get('code', '')
        if base_temp_code == '':
            base_temp_code = code
        else:
            base_temp_code = base_temp_code+'.'+code
        # 处理name
        name = item.get('name', '')
        roles_describe[base_temp_code] = name
        # 如果需要扩展字段可以修改这个字段
        # roles_describe[base_temp_code] = {'name': name}
        # 处理children
        children = item.get('children', [])
        process_child(roles_describe, children, base_temp_code)
        # 重置base_temp_code
        base_temp_code = base_code

@app.task
def provision_tenant_app(tenant_uuid: str, app_id: int):
    pass


@app.task
def provision_user_groups_changed(
    tenant_uuid: str, action: str, user_id: int, group_set: set
):
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
        "Operations": [
            {
                "op": operation,
                "path": "members",
                "value": [{"$ref": None, "value": user_uuid}],
            }
        ],
    }

    ret = patch_group(scim_client, group_uuid, data)
    if ret:
        print(f'group{group_uuid} {operation} user{user_uuid} success')
    else:
        print(f'group{group_uuid} {operation} user{user_uuid} failed')
