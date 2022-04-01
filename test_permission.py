import os
import uuid
import django
import requests
import collections

# 导入settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "arkid.settings")
# 安装django
django.setup()

from inventory.models import(
    Permission, User, UserTenantPermissionAndPermissionGroup,
    PermissionGroup, UserAppPermissionResult,
)
from oauth2_provider.models import get_application_model, get_access_token_model
from app.models import App

Application = get_application_model()
AccessToken = get_access_token_model()

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
                update_single_user_apppermission(app_temp, user, client_id)
            break

def update_single_user_apppermission(app_temp, user, client_id):
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

def app_permission_task(app_temp, api_info):
    response = requests.get(api_info)
    response = response.json()
    # permissions = response.get('permissions')
    permission_jsons = {
        "permissions":[
            {
                "name":"修改数据更新",
                "sort_id":0,
                "type":"api",
                "operation_id":"api_v1_tenant_data_sync_update"
            },
            {
                "name":"创建数据更新",
                "sort_id":1,
                "type":"api",
                "operation_id":"api_v1_tenant_data_sync_create"
            },
            {
                "name":"数据更新",
                "sort_id":2,
                "type":"group",
                "parent":4,
                "container":[
                    0
                ],
                "operation_id":""
            },
            {
                "name":"数据清洗",
                "sort_id":3,
                "type":"group",
                "parent":4,
                "container":[
                    1
                ],
                "operation_id":""
            },
            {
                "name":"数据",
                "sort_id":4,
                "type":"group",
                "container":[

                ],
                "operation_id":""
            },
            {
                "name": "normal-user",
                "sort_id": 5,
                "type": "group",
                "container":[
                    1
                ]
            },
            {
                "name": "tenant-user",
                "sort_id": 6,
                "type": "group",
                "container":[
                    1
                ]
            },
            {
                "name": "platform-user",
                "sort_id": 7,
                "type": "group",
                "container":[
                    1
                ]
            }
        ]
    }
    permission_jsons = permission_jsons.get('permissions')
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
    old_permissions = Permission.valid_objects.filter(
        tenant=tenant,
        app=app_temp,
        content_type=None,
        permission_category='API',
        is_system_permission=True,
        base_code=base_code,
    )
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
    old_permissiongroups = PermissionGroup.valid_objects.filter(
        title=base_title,
        tenant=tenant,
        app=app_temp,
        is_system_group=True,
        base_code=base_code,
        is_update=True,
    ).exclude(uuid=base_permission_group.uuid)
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

if __name__ == '__main__':
    client_id = 'NuLbozhXNrMFYpkhKZlfaf724OaoQSSYlACGE5rF'
    user = User.valid_objects.filter(username='admin').first()
    # by_app_client_id_update_permission(client_id)
    update_user_apppermission(client_id, user.id)