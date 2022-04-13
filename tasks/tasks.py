from common.event import Event
import typing
from .celery import app
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

from inventory.models import (
    Permission, User, UserTenantPermissionAndPermissionGroup,
    PermissionGroup, UserAppPermissionResult,
)
from oauth2_provider.models import get_application_model, get_access_token_model
# from webhook.models import WebHook, WebHookTriggerHistory
from common.utils import send_email as send_email_func
from provisioning.constants import ProvisioningType

import json
import uuid
import requests
import collections

Application = get_application_model()
AccessToken = get_access_token_model()

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
    # 处理任务
    permission_task(None, api_info)


@app.task
def by_app_client_id_update_permission(client_id):
    '''
    根据client_id更新所有权限和权限分组，并更新所有的用户权限
    '''
    apps = App.valid_objects.filter(
        type__in=['OIDC-Platform']
    )
    for app_temp in apps:
        ## 更新缓存的权限
        data = app_temp.data
        app_client_id = data.get('client_id', '')
        if app_client_id == client_id:
            openapi_uris = data.get('openapi_uris', '')
            # 处理任务
            if openapi_uris:
                ## 重新更新openapi对应的权限
                app_permission_task(app_temp, openapi_uris)
                ## 重新计算所有用户权限
                app_all_user_permission(app_temp, client_id)
                break


@app.task
def update_user_apppermission(client_id, user_id):
    '''
    更新单个用户的权限
    '''
    user = User.valid_objects.filter(id=user_id).first()
    apps = App.valid_objects.filter(
        type__in=['OIDC-Platform']
    )
    for app_temp in apps:
        ## 更新缓存的权限
        data = app_temp.data
        app_client_id = data.get('client_id', '')
        if app_client_id == client_id:
            openapi_uris = data.get('openapi_uris', '')
            # 处理任务
            if openapi_uris:
                update_single_user_apppermission(app_temp, user)
            break


@app.task
def update_user_apps_permission(app_ids, user_id):
    '''
    更新单个用户的权限(apps)
    '''
    user = User.valid_objects.filter(id=user_id).first()
    apps = App.valid_objects.filter(
        type__in=['OIDC-Platform'],
        id__in=app_ids,
    )
    for app_temp in apps:
        ## 更新缓存的权限
        data = app_temp.data
        client_id = data.get('client_id', '')
        openapi_uris = data.get('openapi_uris', '')
        # 处理任务
        if openapi_uris:
            update_single_user_apppermission(app_temp, user)


@app.task
def update_group_apppermission(app_ids, group_id):
    group = Group.valid_objects.filter(
        id=group_id
    ).first()
    # 取得当前分组的所有子分组
    uuids = [group.uuid]
    group.child_groups(uuids)
    # 计算出用户
    auth_users = User.valid_objects.filter(
        groups__uuid__in=uuids
    )
    if auth_users:
        apps = App.valid_objects.filter(
            type__in=['OIDC-Platform'],
            id__in=app_ids,
        )
        for app_temp in apps:
            ## 更新缓存的权限
            data = app_temp.data
            openapi_uris = data.get('openapi_uris', '')
            # 处理任务
            if openapi_uris:
                update_users_apppermission(app_temp, auth_users)


def update_users_apppermission(app_temp, auth_users):
    tenant = app_temp.tenant
    # 取出所有的权限
    data_dict = {}
    permissions = Permission.valid_objects.filter(
        tenant=tenant,
        app=app_temp,
        content_type=None,
        permission_category='API',
        is_system_permission=True,
        base_code=app_temp.name,
    )
    for permission in permissions:
        data_dict[permission.sort_id] = permission
    # 取出所有的权限分组
    permissiongroups = PermissionGroup.valid_objects.filter(
        title=app_temp.name,
        tenant=tenant,
        app=app_temp,
        is_system_group=True,
        base_code=app_temp.name,
        is_update=True,
        parent__isnull=False,
    )
    for permissiongroup in permissiongroups:
        data_dict[permissiongroup.sort_id] = permissiongroup
    # 对数据进行一次排序
    data_dict = collections.OrderedDict(sorted(data_dict.items(), key=lambda obj: obj[0]))
    # 将符合条件的数据进行重新组合
    user_permission_groups = UserTenantPermissionAndPermissionGroup.valid_objects.filter(
        tenant=tenant,
        user__in=auth_users,
    )
    user_permission_info_dict = {}
    user_permission_group_info_dict = {}
    for user_permission_group in user_permission_groups:
        user_id = user_permission_group.user.id
        if user_permission_group.permission:
            if user_id not in user_permission_info_dict.keys():
                user_permission_info_dict[user_id] = []
            permission_info_arr = user_permission_info_dict[user_id]
            permission_info_arr.append(user_permission_group.permission_id)
            user_permission_info_dict[user_id] = permission_info_arr
        else:
            if user_id not in user_permission_group_info_dict.keys():
                user_permission_group_info_dict[user_id] = []
            permission_group_info_arr = user_permission_group_info_dict[user_id]
            permission_group_info_arr.append(user_permission_group.permissiongroup_id)
            user_permission_group_info_dict[user_id] = permission_group_info_arr
    # 计算用户权限和权限分组
    for auth_user in auth_users:
        auth_user_id = auth_user.id
        user_permission_item_dict = user_permission_info_dict.get(auth_user_id, [])
        user_permission_group_item_dict = user_permission_group_info_dict.get(auth_user_id, [])
        result_str = ''
        for data_item in data_dict.values():
            if auth_user.is_superuser:
                data_item.is_pass = 1
            else:
                data_item_id = data_item.id
                if isinstance(data_item, Permission):
                    # 权限
                    if data_item_id in user_permission_item_dict:
                        data_item.is_pass = 1
                    else:
                        if hasattr(data_item, 'is_pass') == False:
                            data_item.is_pass = 0
                else:
                    # 权限分组
                    # 如果用户对某一个权限分组有权限，则对该权限分组内的所有权限有权限
                    if data_item.name == 'normal-user':
                        '''
                        普通用户
                        '''
                        data_item.is_pass = 1
                        container = data_item.container
                        if container:
                            for item in container:
                                data_dict.get(item).is_pass = 1
                    elif data_item.name == 'platform-user' and auth_user.is_platform_user is True:
                        '''
                        平台用户
                        '''
                        data_item.is_pass = 1
                        container = data_item.container
                        if container:
                            for item in container:
                                data_dict.get(item).is_pass = 1
                    elif data_item.name == 'tenant-user' and auth_user.tenants.filter(id=app_temp.tenant.id).exists() is True:
                        '''
                        租户用户
                        '''
                        data_item.is_pass = 1
                        container = data_item.container
                        if container:
                            for item in container:
                                data_dict.get(item).is_pass = 1
                    elif data_item_id in user_permission_group_item_dict:
                        '''
                        其它分组
                        '''
                        data_item.is_pass = 1
                        container = data_item.container
                        if container:
                            for item in container:
                                data_dict.get(item).is_pass = 1
                    else:
                        data_item.is_pass = 0
        for data_item in data_dict.values():
            result_str = result_str + str(data_item.is_pass)
        # 用户app权限结果
        userapppermissionresult, is_create = UserAppPermissionResult.objects.get_or_create(
            is_del=False,
            tenant=tenant,
            app=app_temp,
            user=auth_user,
        )
        userapppermissionresult.is_update = True
        userapppermissionresult.result = result_str
        userapppermissionresult.save()


def update_single_user_apppermission(app_temp, user):
    tenant = app_temp.tenant
    # 取出所有的权限
    data_dict = {}
    permissions = Permission.valid_objects.filter(
        tenant=tenant,
        app=app_temp,
        content_type=None,
        permission_category='API',
        is_system_permission=True,
        base_code=app_temp.name,
    )
    for permission in permissions:
        if permission.sort_id != -1:
            data_dict[permission.sort_id] = permission
    # 取出所有的权限分组
    permissiongroups = PermissionGroup.valid_objects.filter(
        title=app_temp.name,
        tenant=tenant,
        app=app_temp,
        is_system_group=True,
        base_code=app_temp.name,
        is_update=True,
        parent__isnull=False,
    )
    for permissiongroup in permissiongroups:
        data_dict[permissiongroup.sort_id] = permissiongroup
    # 对数据进行一次排序
    data_dict = collections.OrderedDict(sorted(data_dict.items(), key=lambda obj: obj[0]))
    # 将符合条件的数据进行重新组合
    user_permission_groups = UserTenantPermissionAndPermissionGroup.valid_objects.filter(
        tenant=tenant,
        user=user,
    )
    user_permission_info_dict = {}
    user_permission_group_info_dict = {}
    for user_permission_group in user_permission_groups:
        user_id = user_permission_group.user.id
        if user_permission_group.permission:
            if user_id not in user_permission_info_dict.keys():
                user_permission_info_dict[user_id] = []
            permission_info_arr = user_permission_info_dict[user_id]
            permission_info_arr.append(user_permission_group.permission_id)
            user_permission_info_dict[user_id] = permission_info_arr
        else:
            if user_id not in user_permission_group_info_dict.keys():
                user_permission_group_info_dict[user_id] = []
            permission_group_info_arr = user_permission_group_info_dict[user_id]
            permission_group_info_arr.append(user_permission_group.permissiongroup_id)
            user_permission_group_info_dict[user_id] = permission_group_info_arr
    # 计算用户权限和权限分组
    auth_user = user
    auth_user_id = auth_user.id
    user_permission_item_dict = user_permission_info_dict.get(auth_user_id, [])
    user_permission_group_item_dict = user_permission_group_info_dict.get(auth_user_id, [])
    result_str = ''
    for data_item in data_dict.values():
        if auth_user.is_superuser:
            data_item.is_pass = 1
        else:
            data_item_id = data_item.id
            if isinstance(data_item, Permission):
                # 权限
                if data_item_id in user_permission_item_dict:
                    data_item.is_pass = 1
                else:
                    if hasattr(data_item, 'is_pass') == False:
                        data_item.is_pass = 0
            else:
                # 权限分组
                # 如果用户对某一个权限分组有权限，则对该权限分组内的所有权限有权限
                if data_item.name == 'normal-user':
                    '''
                    普通用户
                    '''
                    data_item.is_pass = 1
                    container = data_item.container
                    if container:
                        for item in container:
                            data_dict.get(item).is_pass = 1
                elif data_item.name == 'platform-user' and auth_user.is_platform_user is True:
                    '''
                    平台用户
                    '''
                    data_item.is_pass = 1
                    container = data_item.container
                    if container:
                        for item in container:
                            data_dict.get(item).is_pass = 1
                elif data_item.name == 'tenant-user' and auth_user.tenants.filter(id=app_temp.tenant.id).exists() is True:
                    '''
                    租户用户
                    '''
                    data_item.is_pass = 1
                    container = data_item.container
                    if container:
                        for item in container:
                            data_dict.get(item).is_pass = 1
                elif data_item_id in user_permission_group_item_dict:
                    '''
                    其它分组
                    '''
                    data_item.is_pass = 1
                    container = data_item.container
                    if container:
                        for item in container:
                            data_dict.get(item).is_pass = 1
                else:
                    data_item.is_pass = 0
    for data_item in data_dict.values():
        result_str = result_str + str(data_item.is_pass)
    # 用户app权限结果
    userapppermissionresult, is_create = UserAppPermissionResult.objects.get_or_create(
        is_del=False,
        tenant=tenant,
        app=app_temp,
        user=auth_user,
    )
    userapppermissionresult.is_update = True
    userapppermissionresult.result = result_str
    userapppermissionresult.save()


def app_all_user_permission(app_temp, client_id):
    tenant = app_temp.tenant
    # 取得当前应用的所有用户权限
    application = Application.objects.filter(
        client_id=client_id 
    ).first()
    if application:
        auth_users = []
        # 分出所有的用户
        access_tokens = AccessToken.objects.filter(
            application=application,
        )
        for access_token in access_tokens:
            access_token_user = access_token.user
            if access_token_user not in auth_users:
                auth_users.append(access_token_user)
        # 取出所有的权限
        data_dict = {}
        permissions = Permission.valid_objects.filter(
            tenant=tenant,
            app=app_temp,
            content_type=None,
            permission_category='API',
            is_system_permission=True,
            base_code=app_temp.name,
        )
        for permission in permissions:
            if permission.sort_id != -1:
                data_dict[permission.sort_id] = permission
        # 取出所有的权限分组
        permissiongroups = PermissionGroup.valid_objects.filter(
            title=app_temp.name,
            tenant=tenant,
            app=app_temp,
            is_system_group=True,
            base_code=app_temp.name,
            is_update=True,
            parent__isnull=False,
        )
        for permissiongroup in permissiongroups:
            data_dict[permissiongroup.sort_id] = permissiongroup
        # 对数据进行一次排序
        data_dict = collections.OrderedDict(sorted(data_dict.items(), key=lambda obj: obj[0]))
        # 将符合条件的数据进行重新组合
        user_permission_groups = UserTenantPermissionAndPermissionGroup.valid_objects.filter(
            tenant=tenant,
            user__in=auth_users,
        )
        user_permission_info_dict = {}
        user_permission_group_info_dict = {}
        for user_permission_group in user_permission_groups:
            user_id = user_permission_group.user.id
            if user_permission_group.permission:
                if user_id not in user_permission_info_dict.keys():
                    user_permission_info_dict[user_id] = []
                permission_info_arr = user_permission_info_dict[user_id]
                permission_info_arr.append(user_permission_group.permission_id)
                user_permission_info_dict[user_id] = permission_info_arr
            else:
                if user_id not in user_permission_group_info_dict.keys():
                    user_permission_group_info_dict[user_id] = []
                permission_group_info_arr = user_permission_group_info_dict[user_id]
                permission_group_info_arr.append(user_permission_group.permissiongroup_id)
                user_permission_group_info_dict[user_id] = permission_group_info_arr
        # 旧用户app权限
        UserAppPermissionResult.valid_objects.filter(
            tenant=tenant,
            app=app_temp,
        ).update(is_update=False)
        # 计算用户权限和权限分组
        for auth_user in auth_users:
            auth_user_id = auth_user.id
            user_permission_item_dict = user_permission_info_dict.get(auth_user_id, [])
            user_permission_group_item_dict = user_permission_group_info_dict.get(auth_user_id, [])
            result_str = ''
            
            for data_item in data_dict.values():
                data_item_id = data_item.id
                if isinstance(data_item, Permission):
                    # 权限
                    if data_item_id in user_permission_item_dict:
                        data_item.is_pass = 1
                    else:
                        if hasattr(data_item, 'is_pass') == False:
                            data_item.is_pass = 0
                else:
                    # 权限分组
                    # 如果用户对某一个权限分组有权限，则对该权限分组内的所有权限有权限
                    if data_item.name == 'normal-user':
                        '''
                        普通用户
                        '''
                        data_item.is_pass = 1
                        container = data_item.container
                        if container:
                            for item in container:
                                data_dict.get(item).is_pass = 1
                    elif data_item.name == 'platform-user' and auth_user.is_platform_user is True:
                        '''
                        平台用户
                        '''
                        data_item.is_pass = 1
                        container = data_item.container
                        if container:
                            for item in container:
                                data_dict.get(item).is_pass = 1
                    elif data_item.name == 'tenant-user' and auth_user.tenants.filter(id=app_temp.tenant.id).exists() is True:
                        '''
                        租户用户
                        '''
                        data_item.is_pass = 1
                        container = data_item.container
                        if container:
                            for item in container:
                                data_dict.get(item).is_pass = 1
                    elif data_item_id in user_permission_group_item_dict:
                        '''
                        其它分组
                        '''
                        data_item.is_pass = 1
                        container = data_item.container
                        if container:
                            for item in container:
                                data_dict.get(item).is_pass = 1
                    else:
                        data_item.is_pass = 0
            for data_item in data_dict.values():
                result_str = result_str + str(data_item.is_pass)
            # 用户app权限结果
            userapppermissionresult, is_create = UserAppPermissionResult.objects.get_or_create(
                is_del=False,
                tenant=tenant,
                app=app_temp,
                user=auth_user,
            )
            userapppermissionresult.is_update = True
            userapppermissionresult.result = result_str
            userapppermissionresult.save()
        UserAppPermissionResult.valid_objects.filter(
            tenant=tenant,
            app=app_temp,
            is_update=False,
        ).delete()


def app_permission_task(app_temp, api_info):
    '''
    三方应用更新权限
    '''
    response = requests.get(api_info)
    response = response.json()
    permission_jsons = response.get('permissions')
    # permission_jsons = {
    #     "permissions":[
    #         {
    #             "name":"修改数据更新",
    #             "sort_id":0,
    #             "type":"api",
    #             "operation_id":"api_v1_tenant_data_sync_update"
    #         },
    #         {
    #             "name":"创建数据更新",
    #             "sort_id":1,
    #             "type":"api",
    #             "operation_id":"api_v1_tenant_data_sync_create"
    #         },
    #         {
    #             "name":"数据更新",
    #             "sort_id":2,
    #             "type":"group",
    #             "parent":4,
    #             "container":[
    #                 0
    #             ],
    #             "operation_id":""
    #         },
    #         {
    #             "name":"数据清洗",
    #             "sort_id":3,
    #             "type":"group",
    #             "parent":4,
    #             "container":[
    #                 1
    #             ],
    #             "operation_id":""
    #         },
    #         {
    #             "name":"数据",
    #             "sort_id":4,
    #             "type":"group",
    #             "container":[

    #             ],
    #             "operation_id":""
    #         },
    #         {
    #             "name": "normal-user",
    #             "sort_id": 5,
    #             "type": "group",
    #             "container":[
    #                 1
    #             ]
    #         },
    #         {
    #             "name": "tenant-user",
    #             "sort_id": 6,
    #             "type": "group",
    #             "container":[
    #                 1
    #             ]
    #         },
    #         {
    #             "name": "platform-user",
    #             "sort_id": 7,
    #             "type": "group",
    #             "container":[
    #                 1
    #             ]
    #         }
    #     ]
    # }
    # permission_jsons = permission_jsons.get('permissions')
    group_permission_jsons = []
    api_permission_jsons = []
    api_permission_dict = {}
    api_permission_obj_dict = {}
    for permission_json in permission_jsons:
        json_type = permission_json.get('type', '')
        operation_id = permission_json.get('operation_id', '')
        if json_type == 'api':
            api_permission_dict[operation_id] = permission_json
            api_permission_jsons.append(permission_json)
        else:
            group_permission_jsons.append(permission_json)
    # 所有的path
    paths = response.get('paths')
    path_keys = paths.keys()
    # 老的权限(全部重置为没更新)
    base_code = app_temp.name
    base_title = app_temp.name
    tenant = app_temp.tenant
    # old_permissions = Permission.valid_objects.filter(
    #     tenant=tenant,
    #     app=app_temp,
    #     content_type=None,
    #     permission_category='API',
    #     is_system_permission=True,
    #     base_code=base_code,
    # )
    old_permissions = Permission.objects.raw("select * from inventory_permission where is_del=0 and content_type_id is NULl and permission_category='API' and is_update=1 and is_system_permission=1 and tenant_id=%s and base_code=%s and app_id=%s", [tenant.id, base_code, app_temp.id])
    for old_permission in old_permissions:
        old_permission.is_update = False
        old_permission.save()
    # 开始更新权限path
    for path_key in path_keys:
        item = paths.get(path_key)
        item_keys = item.keys()
        for item_key in item_keys:
            request_obj = item.get(item_key)
            request_type = item_key
            request_url = path_key
            action = request_obj.get('action')
            summary = request_obj.get('summary', '')
            description = request_obj.get('description')
            operation_id = request_obj.get('operationId')
            codename = 'api_{}'.format(uuid.uuid4())
            # 接口权限对象
            api_permission_obj = api_permission_dict.get(operation_id, None)
            sort_id = -1
            container = []
            parent_sort_id = -1
            if api_permission_obj:
                api_permission_name = api_permission_obj.get('name', '')
                if api_permission_name:
                    summary = api_permission_name
                api_permission_sort_id = api_permission_obj.get('sort_id', -1)
                if api_permission_sort_id != -1:
                    sort_id = api_permission_sort_id
                api_permission_parent = api_permission_obj.get('parent', -1)
                if api_permission_parent != -1:
                    parent_sort_id = api_permission_parent
                api_permission_container = api_permission_obj.get('container', [])
                if api_permission_container:
                    container = api_permission_container
            # 权限创建
            permission, is_create = Permission.objects.get_or_create(
                permission_category='API',
                is_system_permission=True,
                app=app_temp,
                is_del=False,
                operation_id=operation_id
            )
            if is_create is True:
                permission.codename = codename
            permission.name = summary
            permission.content_type = None
            permission.tenant = tenant
            permission.is_update = True
            permission.action = action
            permission.base_code = base_code
            permission.description = description
            permission.request_url = request_url
            permission.request_type = request_type
            permission.sort_id = sort_id
            permission.parent_sort_id = parent_sort_id
            permission.container = container
            permission.save()
            api_permission_obj_dict[sort_id] = permission
    # 开始更新权限group
    # for group_permission_json in group_permission_jsons:
    #     group_permission_name = group_permission_json.get('name', '')
    #     group_permission_parent = group_permission_json.get('parent', -1)
    #     group_permission_sort_id = group_permission_json.get('sort_id', -1)
    #     group_permission_container = group_permission_json.get('container', [])
    #     codename = 'group_{}'.format(uuid.uuid4())
    #     # 权限创建
    #     permission, is_create = Permission.objects.get_or_create(
    #         permission_category='GROUP',
    #         is_system_permission=True,
    #         app=app_temp,
    #         is_del=False,
    #         name=group_permission_name
    #     )
    #     if is_create is True:
    #         permission.codename = codename
    #     permission.content_type = None
    #     permission.tenant = tenant
    #     permission.is_update = True
    #     permission.action = ''
    #     permission.base_code = base_code
    #     permission.description = ''
    #     permission.request_url = ''
    #     permission.request_type = ''
    #     permission.parent_sort_id = group_permission_parent
    #     permission.sort_id = group_permission_sort_id
    #     permission.container = group_permission_container
    #     permission.save()
    # 删掉没更新的权限
    Permission.valid_objects.filter(
        tenant=tenant,
        app=app_temp,
        content_type=None,
        permission_category='API',
        is_system_permission=True,
        base_code=base_code,
        is_update=False,
    ).delete()
    # Permission.objects.raw("select * from inventory_permission where is_del=0 and content_type_id is NULl and permission_category='API' and is_system_permission=1 and tenant_id=%s and base_code=%s and app_id=%s and is_update=0", [tenant.id, base_code, app_temp.id]).delete()
    # 创建顶级权限分组
    base_permission_group, is_create = PermissionGroup.objects.get_or_create(
        is_active=True,
        is_del=False,
        app=app_temp,
        name=base_title,
        en_name=base_code,
        title=base_title,
        base_code=base_code,
        is_system_group=True,
        is_update=True,
        tenant=tenant,
    )
    # 将权限分组的更新状态全部重置为false
    old_permissiongroups = PermissionGroup.objects.raw('select * from inventory_permissiongroup where is_del=0 and title=%s and app_id=%s and is_system_group=1 and base_code=%s and is_update=%s and tenant_id=%s and uuid != %s', [base_title,app_temp.id,base_code,1,tenant.id,base_permission_group.id])
    # old_permissiongroups = PermissionGroup.valid_objects.filter(
    #     title=base_title,
    #     tenant=tenant,
    #     app=app_temp,
    #     is_system_group=True,
    #     base_code=base_code,
    #     is_update=True,
    # ).exclude(uuid=base_permission_group.uuid)
    for old_permissiongroup in old_permissiongroups:
        old_permissiongroup.is_update = False
        old_permissiongroup.save()
    # 处理掉权限分组实体
    for group_permission_json in group_permission_jsons:
        group_permission_name = group_permission_json.get('name', '')
        group_permission_sort_id = group_permission_json.get('sort_id', -1)
        group_permission_parent_sort_id = group_permission_json.get('parent', -1)
        group_permission_container = group_permission_json.get('container', [])
        # parent
        permissiongroup, is_create = PermissionGroup.objects.get_or_create(
            is_del=False,
            tenant=tenant,
            name=group_permission_name,
            is_system_group=True,
            base_code=base_code,
            title=base_title,
            app=app_temp,
        )
        if group_permission_parent_sort_id == -1:
            permissiongroup.parent = base_permission_group
        else:
            parent_group_json = find_group_parent(group_permission_jsons, group_permission_parent_sort_id)
            parent_name = parent_group_json.get('name', '')
            parent_sort_id = parent_group_json.get('sort_id', -1)
            parent_container = parent_group_json.get('container', [])
            parent_parent_sort_id = parent_group_json.get('parent', -1)
            # 检查父分组是否存在，如果不存在要创建，开始
            parent_permissiongroup, is_create = PermissionGroup.objects.get_or_create(
                is_del=False,
                tenant=tenant,
                name=parent_name,
                is_system_group=True,
                base_code=base_code,
                title=base_title,
                app=app_temp,
            )
            parent_permissiongroup.sort_id = parent_sort_id
            parent_permissiongroup.container = parent_container
            parent_permissiongroup.is_update = True
            parent_permissiongroup.parent_sort_id = parent_parent_sort_id
            parent_permissiongroup.save()
            permissiongroup.parent = parent_permissiongroup
            # 检查父分组是否存在，如果不存在要创建，结束
        permissiongroup.sort_id = group_permission_sort_id
        permissiongroup.container = group_permission_container
        permissiongroup.is_update = True
        permissiongroup.parent_sort_id = group_permission_parent_sort_id
        permissiongroup.save()
        # 扩展分组
        permissiongroup.permissions.clear()
        for group_permission_container_item in group_permission_container:
            permissiongroup.permissions.add(api_permission_obj_dict.get(group_permission_container_item))
    # 删掉没更新的分组数据
    # PermissionGroup.objects.raw('select * from inventory_permissiongroup where is_del=0 and title=%s and app_id=%s and is_system_group=1 and base_code=%s and is_update=%s and tenant_id=%s and uuid != %s', [base_title,app_temp.id,base_code,0,tenant.id,base_permission_group.id]).delete()
    PermissionGroup.valid_objects.filter(
        tenant=tenant,
        app=app_temp,
        is_system_group=True,
        is_update=False,
        title=base_title,
        base_code=base_code,
    ).exclude(uuid=base_permission_group.uuid).delete()


def find_group_parent(json_objs, sort_id):
    for json_obj in json_objs:
        if json_obj.get('sort_id') == sort_id:
            return json_obj


def permission_task(app_temp, api_info):
    '''
    执行更改权限任务
    '''
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
        app=app_temp,
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
                permission_category='API',
                is_system_permission=True,
                app=app_temp,
                is_del=False,
                operation_id=operation_id
            )
            if is_create is True:
                permission.codename = codename
            permission.name = summary
            permission.content_type = None
            permission.tenant = None
            permission.is_update = True
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
        app=app_temp,
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
    # 将权限分组的更新状态全部重置为false
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
    return response


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
