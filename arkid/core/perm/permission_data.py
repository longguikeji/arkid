from arkid.core.b64_compress import Compress
from arkid.core.openapi import get_permissions
from arkid.core.models import (
    UserPermissionResult, SystemPermission, User,
    Tenant, App, Permission, UserGroup,
    ExpiringToken,
)
from arkid.core.api import api
from django.db.models import Q

import collections
import requests
import uuid
import jwt
import re
from oauth2_provider.models import Application


class PermissionData(object):
    '''
    权限数据的统一处理类
    '''

    def __init__(self):
        pass

    def update_system_permission(self):
        '''
        更新系统权限
        '''
        # 取得所有的系统权限
        self.update_arkid_system_permission()
        # 更新所有用户的系统权限
        self.update_arkid_all_user_permission()
    
    def update_app_permission(self, tenant_id, app_id):
        '''
        更新应用权限
        '''
        tenant = Tenant.valid_objects.filter(id=tenant_id).first()
        app = App.valid_objects.filter(id=app_id).first()
        if tenant and app:
            app_config = app.config.config
            openapi_uris = app_config.get('openapi_uris', None)
            if openapi_uris:
                # 取得应用所有的权限
                self.update_app_all_permission(tenant, app)
                # 更新应用所有用户权限
                self.update_app_all_user_permission(tenant, app)
    
    def update_only_user_app_permission(self, tenant_id, app_id):
        '''
        仅仅更新用户的应用权限
        '''
        tenant = Tenant.valid_objects.filter(id=tenant_id).first()
        app = App.valid_objects.filter(id=app_id).first()
        if tenant and app:
            self.update_app_all_user_permission(tenant, app)

    def update_tenant_permission(self, tenant_id):
        '''
        更新租户权限
        '''
        tenant = Tenant.valid_objects.filter(id=tenant_id).first()
        if tenant and app:
            # 更新租户的所有用户权限
            self.update_tenant_all_user_permission(tenant)
    
    def get_platfrom_tenant(self):
        '''
        获取平台租户
        '''
        tenant, _ = Tenant.objects.get_or_create(
            slug='',
            name="platform tenant",
        )
        return tenant
    
    def api_system_permission_check(self, tenant, user, operation_id):
        '''
        检查api接口权限
        '''
        systempermission = SystemPermission.valid_objects.filter(tenant=None, is_system=True, operation_id=operation_id, category='api').first()
        if systempermission:
            sort_id = systempermission.sort_id
            permission_result_arr = self.get_permission_result(tenant, user, None)
            if permission_result_arr and len(permission_result_arr) > sort_id and int(permission_result_arr[sort_id]) == 0:
                return False
        return True
    
    def get_permission_result(self, tenant, user, app):
        '''
        取得用户解码后的权限数组
        '''
        userpermissionresult = UserPermissionResult.valid_objects.filter(
            user=user,
            tenant=tenant,
            app=app,
        ).first()
        compress = Compress()
        permission_result_arr = []
        if userpermissionresult:
            permission_result = compress.decrypt(userpermissionresult.result)
            permission_result_arr = list(permission_result)
            return permission_result_arr

    def add_system_permission_to_user(self, tenant_id, user_id, permission_id):
        '''
        给某个用户增加系统权限
        '''
        tenant = Tenant.valid_objects.filter(id=tenant_id).first()
        user = User.valid_objects.filter(id=user_id).first()
        permission = SystemPermission.valid_objects.filter(id=permission_id).first()
        if tenant:
            self.update_arkid_single_user_permission(tenant, user, permission, 1)
        else:
            print('不存在租户或者用户无法更新')
    
    def remove_system_permission_to_user(self, tenant_id, user_id, permission_id):
        '''
        给某个用户删除系统权限
        '''
        tenant = Tenant.valid_objects.filter(id=tenant_id).first()
        user = User.valid_objects.filter(id=user_id).first()
        permission = SystemPermission.valid_objects.filter(id=permission_id).first()
        if tenant and user:
            self.update_arkid_single_user_permission(tenant, user, permission, 0)
        else:
            print('不存在租户或者用户无法更新')

    def update_single_user_system_permission(self, tenant_id, user_id):
        '''
        更新单个用户的系统权限
        '''
        tenant = Tenant.valid_objects.filter(id=tenant_id).first()
        user = User.valid_objects.filter(id=user_id).first()
        if tenant and user:
            self.update_arkid_single_user_permission(tenant, user, None, None)
        else:
            print('不存在租户或者用户无法更新')

    def update_arkid_system_permission(self):
        '''
        更新系统权限
        '''
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
            method = permissions_item.get('method', '')
            url = permissions_item.get('url', '')
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
                    'method': method,
                    'url': url,
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
        ).update(is_del=0)

    def update_arkid_all_user_permission(self, tenant_id=None):
        '''
        更新所有用户权限
        '''
        # 当前的租户
        if tenant_id is None:
            tenant = self.get_platfrom_tenant()
        else:
            tenant = Tenant.valid_objects.filter(id=tenant_id).first()
        # 取得当前租户的所有用户
        auth_users = User.valid_objects.filter(tenant_id=tenant.id)
        # 区分出那些人是管理员
        systempermission = SystemPermission.objects.filter(tenant=tenant, code=tenant.admin_perm_code, is_system=True).first()
        userpermissionresults = UserPermissionResult.valid_objects.filter(
            tenant=tenant,
            app=None,
        )
        userpermissionresults_dict = {}
        compress = Compress()
        for userpermissionresult in userpermissionresults:
            userpermissionresults_dict[userpermissionresult.user.id.hex] = userpermissionresult
        for auth_user in auth_users:
            # 权限鉴定
            if auth_user.is_superuser:
                auth_user.is_tenant_admin = True
            else:
                if auth_user.id.hex in userpermissionresults_dict:
                    userpermissionresult_obj = userpermissionresults_dict.get(auth_user.id.hex)
                    auth_user_permission_result = compress.decrypt(userpermissionresult_obj.result)
                    auth_user_permission_result_arr = list(auth_user_permission_result)
                    
                    check_result = int(auth_user_permission_result_arr[systempermission.sort_id])
                    if check_result == 1:
                        auth_user.is_tenant_admin = True
                    else:
                        auth_user.is_tenant_admin = False
                else:
                    auth_user.is_tenant_admin = False
        # 权限数据
        system_permissions = SystemPermission.objects.order_by('sort_id')
        data_dict = {}
        data_group_parent_child = {}
        for system_permission in system_permissions:
            data_dict[system_permission.sort_id] = system_permission
            if system_permission.parent:
                parent_id_hex = system_permission.parent.id.hex
                if parent_id_hex not in data_group_parent_child:
                    data_group_parent_child[parent_id_hex] = [system_permission]
                else:
                    temp_data_group = data_group_parent_child[parent_id_hex]
                    temp_data_group.append(system_permission)
                    data_group_parent_child[parent_id_hex] = temp_data_group
        data_dict = collections.OrderedDict(sorted(data_dict.items(), key=lambda obj: obj[0]))
        # 计算每一个用户的权限情况
        for auth_user in auth_users:
            permission_result = ''
            permission_result_arr = []
            if auth_user.id.hex in userpermissionresults_dict:
                # 解析权限字符串
                userpermissionresult_obj = userpermissionresults_dict.get(auth_user.id.hex)
                permission_result = compress.decrypt(userpermissionresult_obj.result)
                if permission_result:
                    permission_result_arr = list(permission_result)
                    if len(permission_result_arr) < len(data_dict.keys()):
                        # 如果原来的权限数目比较少，增加了新的权限，需要先补0
                        diff = len(data_dict.keys()) - len(permission_result_arr)
                        for i in range(diff):
                            permission_result_arr.append(0)
                    # 提前把有父子关系的权限处理好
                    for data_item in data_dict.values():
                        sort_id = data_item.sort_id
                        sort_id_result = int(permission_result_arr[sort_id])
                        if sort_id_result == 1:
                            if data_item.category == 'group':
                                # 如果用户对某一个分组有权限，则对该分组的所有下属分组都有权限。
                                group_id_hex = data_item.id.hex
                                if group_id_hex in data_group_parent_child:
                                    # 递归<查找>
                                    await_result = []
                                    self.process_chilld(data_group_parent_child, group_id_hex, await_result)
                                    for parent_child_item in await_result:
                                        parent_child_sort_id = parent_child_item.sort_id
                                        permission_result_arr[parent_child_sort_id] = '1'
                    # 权限更新设置
                    for data_item in data_dict.values():
                        sort_id = data_item.sort_id
                        sort_id_result = int(permission_result_arr[sort_id])
                        if sort_id_result == 1:
                            data_item.is_pass = 1
                        else:
                            data_item.is_pass = 0
            else:
                for data_item in data_dict.values():
                    data_item.is_pass = 0
            # 权限查验
            for data_item in data_dict.values():
                # 如果是通过就不查验
                if hasattr(data_item, 'is_pass') == True and data_item.is_pass == 1:
                    continue
                # 如果是超级管理员直接就通过
                if auth_user.is_superuser:
                    data_item.is_pass = 1
                else:
                    if data_item.name == 'normal-user':
                        data_item.is_pass = 1
                        describe = data_item.describe
                        container = describe.get('sort_ids')
                        if container:
                            for item in container:
                                data_dict.get(item).is_pass = 1
                        else:
                            data_dict.get(item).is_pass = 0
                    elif data_item.name == 'tenant-admin' and auth_user.is_tenant_admin:
                        data_item.is_pass = 1
                        describe = data_item.describe
                        container = describe.get('sort_ids')
                        if container:
                            for item in container:
                                data_dict.get(item).is_pass = 1
                        else:
                            data_dict.get(item).is_pass = 0
                    elif data_item.name == 'platform-admin':
                        data_item.is_pass = 0
                    elif hasattr(data_item, 'is_pass') == False:
                        data_item.is_pass = 0
                    else:
                        data_item.is_pass = 0
                # 产生结果字符串
                if permission_result:
                    for data_item in data_dict.values():
                        permission_result_arr[data_item.sort_id] = data_item.is_pass
                else:
                    for data_item in data_dict.values():
                        permission_result_arr.append(data_item.is_pass)
                permission_result = "".join(map(str, permission_result_arr))
                compress_str_result = compress.encrypt(permission_result)
                if compress_str_result:
                    userpermissionresult, is_create = UserPermissionResult.objects.get_or_create(
                        is_del=False,
                        user=auth_user,
                        tenant=tenant,
                        app=None,
                    )
                    userpermissionresult.is_update = True
                    userpermissionresult.result = compress_str_result
                    userpermissionresult.save()

    def update_arkid_single_user_permission(self, tenant, auth_user, pass_permission, permission_value):
        '''
        更新指定用户系统权限
        '''
        is_tenant_admin = tenant.has_admin_perm(auth_user)
        system_permissions = SystemPermission.objects.order_by('sort_id')
        data_dict = {}
        data_group_parent_child = {}
        for system_permission in system_permissions:
            data_dict[system_permission.sort_id] = system_permission
            if system_permission.parent:
                parent_id_hex = system_permission.parent.id.hex
                if parent_id_hex not in data_group_parent_child:
                    data_group_parent_child[parent_id_hex] = [system_permission]
                else:
                    temp_data_group = data_group_parent_child[parent_id_hex]
                    temp_data_group.append(system_permission)
                    data_group_parent_child[parent_id_hex] = temp_data_group
        # 取得当前用户权限数据
        userpermissionresult = UserPermissionResult.valid_objects.filter(
            user=auth_user,
            tenant=tenant,
            app=None,
        ).first()
        compress = Compress()
        permission_result = ''
        if userpermissionresult:
            permission_result = compress.decrypt(userpermissionresult.result)
        # 对数据进行一次排序
        data_dict = collections.OrderedDict(sorted(data_dict.items(), key=lambda obj: obj[0]))
        permission_result_arr = []
        if permission_result:
            permission_result_arr = list(permission_result)
            if len(permission_result_arr) < len(data_dict.keys()):
                # 如果原来的权限数目比较少，增加了新的权限，需要先补0
                diff = len(data_dict.keys()) - len(permission_result_arr)
                for i in range(diff):
                    permission_result_arr.append(0)
            # 提前把有父子关系的权限处理好
            for data_item in data_dict.values():
                sort_id = data_item.sort_id
                sort_id_result = int(permission_result_arr[sort_id])
                if sort_id_result == 1:
                    if data_item.category == 'group':
                        # 如果用户对某一个分组有权限，则对该分组的所有下属分组都有权限。
                        group_id_hex = data_item.id.hex
                        if group_id_hex in data_group_parent_child:
                            # 递归<查找>
                            await_result = []
                            self.process_chilld(data_group_parent_child, group_id_hex, await_result)
                            for parent_child_item in await_result:
                                parent_child_sort_id = parent_child_item.sort_id
                                permission_result_arr[parent_child_sort_id] = '1'
            # 权限更新设置
            for data_item in data_dict.values():
                sort_id = data_item.sort_id
                sort_id_result = int(permission_result_arr[sort_id])
                if sort_id_result == 1:
                    # 这里权限同步更新
                    data_item.is_pass = 1
                else:
                    data_item.is_pass = 0
        # 权限检查
        for data_item in data_dict.values():
            if pass_permission != None and data_item.id == pass_permission.id:
                data_item.is_pass = permission_value
                if data_item.category == 'group' and data_item.container.all():
                    for data_item_child_api in data_item.container.all():
                        temp_data_item = data_item.get(data_item_child_api.sort_id, None)
                        if temp_data_item:
                            temp_data_item.is_pass = permission_value
                continue
            # 如果是通过就不查验
            if hasattr(data_item, 'is_pass') == True and data_item.is_pass == 1:
                continue
            # 如果是超级管理员直接就通过
            if auth_user.is_superuser:
                data_item.is_pass = 1
            else:
                if data_item.name == 'normal-user':
                    data_item.is_pass = 1
                    describe = data_item.describe
                    container = describe.get('sort_ids')
                    if container:
                        for item in container:
                            data_dict.get(item).is_pass = 1
                    else:
                        data_dict.get(item).is_pass = 0
                elif data_item.name == 'tenant-admin' and is_tenant_admin:
                    data_item.is_pass = 1
                    describe = data_item.describe
                    container = describe.get('sort_ids')
                    if container:
                        for item in container:
                            data_dict.get(item).is_pass = 1
                    else:
                        data_dict.get(item).is_pass = 0
                elif data_item.name == 'platform-admin':
                    data_item.is_pass = 0
                elif hasattr(data_item, 'is_pass') == False:
                    data_item.is_pass = 0
                else:
                    data_item.is_pass = 0
        # 产生结果字符串
        if permission_result:
            for data_item in data_dict.values():
                permission_result_arr[data_item.sort_id] = data_item.is_pass
        else:
            for data_item in data_dict.values():
                permission_result_arr.append(data_item.is_pass)
        permission_result = "".join(map(str, permission_result_arr))
        compress_str_result = compress.encrypt(permission_result)
        if compress_str_result:
            userpermissionresult, is_create = UserPermissionResult.objects.get_or_create(
                is_del=False,
                user=auth_user,
                tenant=tenant,
                app=None,
            )
            userpermissionresult.is_update = True
            userpermissionresult.result = compress_str_result
            userpermissionresult.save()
    
    def process_chilld(self, find_dict, id_hex, result):
        '''
        递归查找分组
        '''
        items = find_dict.get(id_hex, None)
        if items is None:
            return
        else:
            for item in items:
                result.append(item)
                item_id_hex = item.id.hex
                self.process_chilld(find_dict, item_id_hex, result)

    def get_app_permission_by_api_url(self, app):
        '''
        根据应用的接口地址获取应用的权限转换为列表
        '''
        app_config = app.config.config
        openapi_uris = app_config.get('openapi_uris', '')
        response = requests.get(openapi_uris)
        response = response.json()
        permission_jsons = response.get('permissions', [])
        return permission_jsons

    def update_app_all_permission(self, tenant, app):
        '''
        更新应用的所有权限
        '''
        permissions_data = self.get_app_permission_by_api_url(app)
        if permissions_data:
            group_data = []
            api_data = []
            old_permissions = Permission.valid_objects.filter(
                Q(code__icontains='group_role') | Q(category='api'),
                tenant=tenant,
                app=app,
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
                    permission = Permission.valid_objects.filter(
                        tenant=tenant,
                        app=app,
                        category='group',
                        is_system=True,
                        name=name,
                        code__icontains='group_role',
                    ).first()
                    if not permission:
                        permission = Permission()
                        permission.app = app
                        permission.category = 'group'
                        permission.is_system = True
                        permission.name = name
                        permission.code = 'group_role_{}'.format(uuid.uuid4())
                        permission.tenant = tenant
                        permission.operation_id = ''
                        permission.describe = {}
                    permission.is_update = True
                    permission.save()
                else:
                    api_data.append(permissions_item)
                    permission, is_create = Permission.objects.get_or_create(
                        tenant=tenant,
                        app=app,
                        category='api',
                        is_system=True,
                        is_del=False,
                        operation_id=operation_id,
                    )
                    if is_create is True:
                        permission.code = 'api_{}'.format(uuid.uuid4())
                    permission.name = name
                    permission.describe = {}
                    permission.is_update = True
                    permission.save()
                permissions_item['sort_real_id'] = permission.sort_id
                permissions_item['permission'] = permission
            # 单独处理分组问题
            for group_item in group_data:
                container = group_item.get('container', [])
                group_permission = group_item.get('permission', None)
                group_sort_ids = []
                for api_item in api_data:
                    sort_id = api_item.get('sort_id', 0)
                    sort_real_id = api_item.get('sort_real_id', 0)
                    api_permission = api_item.get('permission', None)

                    if sort_id in container and api_permission:
                        group_permission.container.add(api_permission)
                        group_sort_ids.append(sort_real_id)
                # parent
                parent = group_item.get('parent', -1)
                describe = {'sort_ids': group_sort_ids}
                if parent != -1:
                    parent_real = None
                    for group_next in group_data:
                        sort_id = group_next.get('sort_id', 0)
                        sort_real_id = group_next.get('sort_real_id', 0)
                        group_next_permission = group_next.get('permission', None)
                        if sort_id == parent and group_next_permission:
                            group_permission.parent = group_next_permission
                            describe['parent'] = sort_real_id
                            break
                else:
                    group_permission.parent = None
                group_permission.describe = describe
                group_permission.save()
            # 权限更新
            Permission.valid_objects.filter(
                Q(code__icontains='group_role') | Q(category='api'),
                tenant=tenant,
                app=app,
                is_system=True,
                is_update=False
            ).update(is_del=0)

    def update_app_all_user_permission(self, tenant, app):
        '''
        更新应用所有用户权限
        '''
        # 取得当前租户的所有用户
        auth_users = User.valid_objects.filter(tenant_id=tenant.id)
        # 区分出那些人是管理员
        systempermission = SystemPermission.valid_objects.filter(tenant=tenant, code=tenant.admin_perm_code, is_system=True).first()
        # app的
        userpermissionresults = UserPermissionResult.valid_objects.filter(
            tenant=tenant,
            app=app,
        )
        userpermissionresults_dict = {}
        compress = Compress()
        for userpermissionresult in userpermissionresults:
            userpermissionresults_dict[userpermissionresult.user.id.hex] = userpermissionresult
        # 管理权限在arkidpermission表里
        system_userpermissionresults = UserPermissionResult.valid_objects.filter(
            tenant=tenant,
            app=None,
        )
        system_userpermissionresults_dict = {}
        for system_userpermissionresult in system_userpermissionresults:
            system_userpermissionresults_dict[system_userpermissionresult.user.id.hex] = system_userpermissionresult
        for auth_user in auth_users:
            # 权限鉴定
            if auth_user.is_superuser:
                auth_user.is_tenant_admin = True
            else:
                if auth_user.id.hex in system_userpermissionresults_dict:
                    system_userpermissionresults_obj = system_userpermissionresults_dict.get(auth_user.id.hex)
                    auth_user_permission_result = compress.decrypt(system_userpermissionresults_obj.result)

                    auth_user_permission_result_arr = list(auth_user_permission_result)
                    check_result = int(auth_user_permission_result_arr[systempermission.sort_id])

                    if check_result == 1:
                        auth_user.is_tenant_admin = True
                    else:
                        auth_user.is_tenant_admin = False
                else:
                    auth_user.is_tenant_admin = False
        # 权限数据
        permissions = Permission.objects.filter(app=app).order_by('sort_id')
        data_dict = {}
        data_group_parent_child = {}
        for permission in permissions:
            data_dict[permission.sort_id] = permission
            if permission.parent:
                parent_id_hex = permission.parent.id.hex
                if parent_id_hex not in data_group_parent_child:
                    data_group_parent_child[parent_id_hex] = [permission]
                else:
                    temp_data_group = data_group_parent_child[parent_id_hex]
                    temp_data_group.append(permission)
                    data_group_parent_child[parent_id_hex] = temp_data_group
        data_dict = collections.OrderedDict(sorted(data_dict.items(), key=lambda obj: obj[0]))
        # 计算每一个用户的权限情况
        for auth_user in auth_users:
            permission_result = ''
            permission_result_arr = []
            if auth_user.id.hex in userpermissionresults_dict:
                # 解析权限字符串
                userpermissionresult_obj = userpermissionresults_dict.get(auth_user.id.hex)
                permission_result = compress.decrypt(userpermissionresult_obj.result)
                if permission_result:
                    permission_result_arr = list(permission_result)
                    if len(permission_result_arr) < len(data_dict.keys()):
                        # 如果原来的权限数目比较少，增加了新的权限，需要先补0
                        diff = len(data_dict.keys()) - len(permission_result_arr)
                        for i in range(diff):
                            permission_result_arr.append(str(0))
                    # 提前把有父子关系的权限处理好
                    for data_item in data_dict.values():
                        sort_id = data_item.sort_id
                        sort_id_result = int(permission_result_arr[sort_id])
                        if sort_id_result == 1:
                            if data_item.category == 'group':
                                # 如果用户对某一个分组有权限，则对该分组的所有下属分组都有权限。
                                group_id_hex = data_item.id.hex
                                if group_id_hex in data_group_parent_child:
                                    # 递归<查找>
                                    await_result = []
                                    self.process_chilld(data_group_parent_child, group_id_hex, await_result)
                                    for parent_child_item in await_result:
                                        parent_child_sort_id = parent_child_item.sort_id
                                        permission_result_arr[parent_child_sort_id] = '1'
                    # 权限更新设置
                    for data_item in data_dict.values():
                        sort_id = data_item.sort_id
                        sort_id_result = int(permission_result_arr[sort_id])
                        if sort_id_result == 1:
                            data_item.is_pass = 1
                        else:
                            data_item.is_pass = 0
            else:
                for data_item in data_dict.values():
                    data_item.is_pass = 0
            # 权限查验
            for data_item in data_dict.values():
                # 如果是通过就不查验
                if hasattr(data_item, 'is_pass') == True and data_item.is_pass == 1:
                    continue
                # 如果是超级管理员直接就通过
                if auth_user.is_superuser:
                    data_item.is_pass = 1
                else:
                    if tenant == data_item.tenant:
                        if data_item.name == 'normal-user':
                            data_item.is_pass = 1
                            describe = data_item.describe
                            container = describe.get('sort_ids')
                            if container:
                                for item in container:
                                    data_dict.get(item).is_pass = 1
                            else:
                                data_item.is_pass = 0
                        elif data_item.name == 'tenant-admin' and auth_user.is_tenant_admin:
                            data_item.is_pass = 1
                            describe = data_item.describe
                            container = describe.get('sort_ids')
                            if container:
                                for item in container:
                                    data_dict.get(item).is_pass = 1
                            else:
                                data_item.is_pass = 0
                        elif data_item.name == 'platform-admin':
                            # 平台管理员默认有所有权限所有这里没必要做处理
                            data_item.is_pass = 0
                        elif hasattr(data_item, 'is_pass') == False:
                            data_item.is_pass = 0
                        else:
                            data_item.is_pass = 0
                    else:
                        # 如果是开放权限，不同租户就只放0
                        data_item.is_pass = 0
            # 产生结果字符串
            if permission_result:
                for data_item in data_dict.values():
                    permission_result_arr[data_item.sort_id] = data_item.is_pass
            else:
                for data_item in data_dict.values():
                    permission_result_arr.append(data_item.is_pass)
            permission_result = "".join(map(str, permission_result_arr))
            compress_str_result = compress.encrypt(permission_result)
            if compress_str_result:
                userpermissionresult, is_create = UserPermissionResult.objects.get_or_create(
                    is_del=False,
                    user=auth_user,
                    tenant=tenant,
                    app=app,
                )
                userpermissionresult.is_update = True
                userpermissionresult.result = compress_str_result
                userpermissionresult.save()

    def update_single_user_app_permission(self, tenant_id, user_id, app_id):
        '''
        更新单个用户的应用权限
        '''
        tenant = Tenant.valid_objects.filter(id=tenant_id).first()
        user = User.valid_objects.filter(id=user_id).first()
        app = App.valid_objects.filter(id=app_id).first()
        if tenant and user and app:
            self.update_app_single_user_permission_detail(tenant, user, app, None, None)
        else:
            print('不存在租户或者用户或者应用无法更新')
    
    def update_app_single_user_permission_detail(self, tenant, auth_user, app, pass_permission, permission_value):
        '''
        更新指定用户应用权限
        '''
        is_tenant_admin = tenant.has_admin_perm(auth_user)
        permissions = Permission.objects.filter(app=app).order_by('sort_id')
        data_dict = {}
        data_group_parent_child = {}
        for permission in permissions:
            data_dict[permission.sort_id] = permission
            if permission.parent:
                parent_id_hex = permission.parent.id.hex
                if parent_id_hex not in data_group_parent_child:
                    data_group_parent_child[parent_id_hex] = [permission]
                else:
                    temp_data_group = data_group_parent_child[parent_id_hex]
                    temp_data_group.append(permission)
                    data_group_parent_child[parent_id_hex] = temp_data_group
        # 取得当前用户权限数据
        userpermissionresult = UserPermissionResult.valid_objects.filter(
            user=auth_user,
            tenant=tenant,
            app=app,
        ).first()
        compress = Compress()
        permission_result = ''
        if userpermissionresult:
            permission_result = compress.decrypt(userpermissionresult.result)
        # 对数据进行一次排序
        data_dict = collections.OrderedDict(sorted(data_dict.items(), key=lambda obj: obj[0]))

        permission_result_arr = []
        if permission_result:
            permission_result_arr = list(permission_result)
            if len(permission_result_arr) < len(data_dict.keys()):
                # 如果原来的权限数目比较少，增加了新的权限，需要先补0
                diff = len(data_dict.keys()) - len(permission_result_arr)
                for i in range(diff):
                    permission_result_arr.append(0)
            # 提前把有父子关系的权限处理好
            for data_item in data_dict.values():
                sort_id = data_item.sort_id
                sort_id_result = int(permission_result_arr[sort_id])
                if sort_id_result == 1:
                    if data_item.category == 'group':
                        # 如果用户对某一个分组有权限，则对该分组的所有下属分组都有权限。
                        group_id_hex = data_item.id.hex
                        if group_id_hex in data_group_parent_child:
                            # 递归<查找>
                            await_result = []
                            self.process_chilld(data_group_parent_child, group_id_hex, await_result)
                            for parent_child_item in await_result:
                                parent_child_sort_id = parent_child_item.sort_id
                                permission_result_arr[parent_child_sort_id] = '1'
            # 权限更新设置
            for data_item in data_dict.values():
                sort_id = data_item.sort_id
                sort_id_result = int(permission_result_arr[sort_id])
                if sort_id_result == 1:
                    data_item.is_pass = 1
                else:
                    data_item.is_pass = 0
        # 权限检查
        for data_item in data_dict.values():
            # 跳过的数据
            if pass_permission != None and data_item.id == pass_permission.id:
                data_item.is_pass = permission_value
                if data_item.category == 'group' and data_item.container.all():
                    for data_item_child_api in data_item.container.all():
                        temp_data_item = data_item.get(data_item_child_api.sort_id, None)
                        if temp_data_item:
                            temp_data_item.is_pass = permission_value
                continue
            # 如果是通过就不查验
            if hasattr(data_item, 'is_pass') == True and data_item.is_pass == 1:
                continue
            # 如果是超级管理员直接就通过
            if auth_user.is_superuser:
                data_item.is_pass = 1
            else:
                if tenant == data_item.tenant:
                    if data_item.name == 'normal-user':
                        data_item.is_pass = 1
                        describe = data_item.describe
                        container = describe.get('sort_ids')
                        if container:
                            for item in container:
                                data_dict.get(item).is_pass = 1
                        else:
                            data_item.is_pass = 0
                    elif data_item.name == 'tenant-admin' and is_tenant_admin:
                        data_item.is_pass = 1
                        describe = data_item.describe
                        container = describe.get('sort_ids')
                        if container:
                            for item in container:
                                data_dict.get(item).is_pass = 1
                        else:
                            data_item.is_pass = 0
                    elif data_item.name == 'platform-admin':
                        # 平台管理员默认有所有权限所有这里没必要做处理
                        data_item.is_pass = 0
                    elif hasattr(data_item, 'is_pass') == False:
                        data_item.is_pass = 0
                    else:
                        data_item.is_pass = 0
                else:
                    # 如果是开放权限，不同租户就只放0
                    data_item.is_pass = 0
        # 产生结果字符串
        if permission_result:
            for data_item in data_dict.values():
                permission_result_arr[data_item.sort_id] = data_item.is_pass
        else:
            for data_item in data_dict.values():
                permission_result_arr.append(data_item.is_pass)
        permission_result = "".join(map(str, permission_result_arr))
        compress_str_result = compress.encrypt(permission_result)
        if compress_str_result:
            userpermissionresult, is_create = UserPermissionResult.objects.get_or_create(
                is_del=False,
                user=auth_user,
                tenant=tenant,
                app=app,
            )
            userpermissionresult.is_update = True
            userpermissionresult.result = compress_str_result
            userpermissionresult.save()

    def add_app_permission_to_user(self, tenant_id, app_id, user_id, permission_id):
        '''
        给某个用户增加应用权限
        '''
        tenant = Tenant.valid_objects.filter(id=tenant_id).first()
        user = User.valid_objects.filter(id=user_id).first()
        app = App.valid_objects.filter(id=app_id).first()
        permission = Permission.valid_objects.filter(id=permission_id).first()
        if tenant and user:
            self.update_app_single_user_permission_detail(tenant, user, app, permission, 1)
        else:
            print('不存在租户或者用户无法更新')
    
    def remove_app_permission_to_user(self, tenant_id, app_id, user_id, permission_id):
        '''
        给某个用户删除应用权限
        '''
        tenant = Tenant.valid_objects.filter(id=tenant_id).first()
        user = User.valid_objects.filter(id=user_id).first()
        app = App.valid_objects.filter(id=app_id).first()
        permission = Permission.valid_objects.filter(id=permission_id).first()
        if tenant and user:
            self.update_app_single_user_permission_detail(tenant, user, app, permission, 0)
        else:
            print('不存在租户或者用户无法更新')

    def update_tenant_all_user_permission(self, tenant):
        '''
        更新租户的所有用户权限
        '''
        # 取得当前租户的所有用户
        auth_users = User.valid_objects.filter(tenant_id=tenant.id)
        userpermissionresults = UserPermissionResult.valid_objects.filter(
            tenant=tenant,
            is_self_create=True,
        )
        userpermissionresults_dict = {}
        compress = Compress()
        for userpermissionresult in userpermissionresults:
            userpermissionresults_dict[userpermissionresult.user.id.hex] = userpermissionresult
        # 取得当前租户的所有自建立租户权限
        permissions = Permission.valid_objects.filter(tenant=tenant, is_system=False).order_by('sort_id')
        data_dict = {}
        data_group_parent_child = {}
        for permission in permissions:
            data_dict[permission.sort_id] = permission
            if permission.parent:
                parent_id_hex = permission.parent.id.hex
                if parent_id_hex not in data_group_parent_child:
                    data_group_parent_child[parent_id_hex] = [permission]
                else:
                    temp_data_group = data_group_parent_child[parent_id_hex]
                    temp_data_group.append(permission)
                    data_group_parent_child[parent_id_hex] = temp_data_group
        data_dict = collections.OrderedDict(sorted(data_dict.items(), key=lambda obj: obj[0]))
    
    def get_permissions_by_search(self, tenant_id, app_id, user_id, group_id, login_user, parent_id=None, is_only_show_group=False, app_name=None, category=None):
        '''
        根据应用，用户，分组查权限(要根据用户身份显示正确的列表)
        '''
        permissions = Permission.valid_objects.filter(
            Q(tenant_id=tenant_id)|Q(is_open=True)
        )
        systempermissions = SystemPermission.valid_objects
        if is_only_show_group:
            permissions = permissions.filter(
                category='group'
            )
            systempermissions = systempermissions.filter(
                category='group'
            )
            if parent_id:
                systempermissions = systempermissions.filter(parent_id=parent_id)
                permissions = permissions.filter(parent_id=parent_id)
            else:
                systempermissions = systempermissions.filter(parent_id__isnull=True)
                permissions = permissions.filter(parent_id__isnull=True)
        if app_id and app_id == 'arkid':
            # arkid没有应用权限
            app_id = None
            systempermissions = systempermissions.filter(tenant_id=None)
            permissions = permissions.filter(app_id=None)
        compress = Compress()
        if app_id is None and user_id is None and group_id is None and login_user:
            # 需要正确展现用户的id
            user_id = str(login_user.id)
        if app_name:
            permissions = permissions.filter(app__name=app_name)
        if category:
            permissions = permissions.filter(category=category)
            systempermissions = systempermissions.filter(category=category)
        if app_id or user_id or group_id:
            if app_id:
                app = App.valid_objects.filter(
                    id=app_id
                ).first()
                tenant_uid = uuid.UUID(tenant_id)
                if app and app.entry_permission:
                    systempermissions = systempermissions.filter(id=app.entry_permission.id)
                    permissions = permissions.filter(app_id=app_id)
                    if app.tenant.id != tenant_uid:
                        # 只展示为1的系统权限
                        userpermissionresult = UserPermissionResult.valid_objects.filter(
                            app=None,
                            user=login_user,
                            tenant_id=tenant_id
                        ).first()
                        permission_sort_ids = []
                        if userpermissionresult:
                            permission_result = compress.decrypt(userpermissionresult.result)
                            permission_result_arr = list(permission_result)
                            for index, item in enumerate(permission_result_arr):
                                if int(item) == 1:
                                    permission_sort_ids.append(index)
                        if len(permission_sort_ids) == 0:
                            systempermissions = systempermissions.filter(id__isnull=True)
                        else:
                            systempermissions = systempermissions.filter(sort_id__in=permission_sort_ids)
                        # 只展示为1的应用权限
                        userpermissionresult = UserPermissionResult.valid_objects.filter(
                            app=app,
                            user=login_user,
                            tenant_id=tenant_id
                        ).first()
                        permission_sort_ids = []
                        if userpermissionresult:
                            permission_result = compress.decrypt(userpermissionresult.result)
                            permission_result_arr = list(permission_result)
                            for index, item in enumerate(permission_result_arr):
                                if int(item) == 1:
                                    permission_sort_ids.append(index)
                        if len(permission_sort_ids) == 0:
                            permissions = permissions.filter(id__isnull=True)
                        else:
                            permissions = permissions.filter(sort_id__in=permission_sort_ids)
            if user_id:
                # 系统权限
                userpermissionresult = UserPermissionResult.valid_objects.filter(
                    user_id=user_id,
                    tenant_id=tenant_id,
                    app=None
                ).first()
                permission_sort_ids = []
                if userpermissionresult:
                    permission_result = compress.decrypt(userpermissionresult.result)
                    permission_result_arr = list(permission_result)
                    for index, item in enumerate(permission_result_arr):
                        if int(item) == 1:
                            permission_sort_ids.append(index)
                if len(permission_sort_ids) == 0:
                    systempermissions = systempermissions.filter(id__isnull=True)
                else:
                    systempermissions = systempermissions.filter(sort_id__in=permission_sort_ids)
                # 应用权限
                userpermissionresult = UserPermissionResult.valid_objects.filter(
                    user_id=user_id,
                    tenant_id=tenant_id,
                    app__isnull=False
                ).first()
                permission_sort_ids = []
                if userpermissionresult:
                    permission_result = compress.decrypt(userpermissionresult.result)
                    permission_result_arr = list(permission_result)
                    for index, item in enumerate(permission_result_arr):
                        if int(item) == 1:
                            permission_sort_ids.append(index)
                if len(permission_sort_ids) == 0:
                    permissions = permissions.filter(id__isnull=True)
                else:
                    permissions = permissions.filter(sort_id__in=permission_sort_ids)
            if group_id:
                usergroup = UserGroup.valid_objects.filter(id=group_id).first()
                if usergroup:
                    group_permission = usergroup.permission
                    if group_permission is None:
                        systempermissions = systempermissions.filter(id__isnull=True)
                    else:
                        systempermissions = systempermissions.filter(id=group_permission.id)
                    # 没有应用分组，只有系统分组
                    permissions = permissions.filter(id__isnull=True)
        else:
            systempermissions = systempermissions.filter(Q(tenant__isnull=True)|Q(tenant_id=tenant_id))
        return list(systempermissions)+list(permissions)

    def get_permission_str(self, user, tenant_id, app_id, is_64=False):
        '''
        获取权限字符串
        '''
        compress = Compress()
        userpermissionresults = UserPermissionResult.valid_objects.filter(
            user=user,
            tenant_id=tenant_id,
        )
        if app_id:
            userpermissionresult = userpermissionresults.filter(
                app_id=app_id,
            ).first()
        else:
            userpermissionresult = userpermissionresults.filter(   
                app__isnull=True,
            ).first()
        if userpermissionresult:
            if is_64:
                permission_result = userpermissionresult.result
            else:
                permission_result = compress.decrypt(userpermissionresult.result)
            return {'result': permission_result}
        else:
            return {'result': ''}


    def has_admin_perm(self, tenant, user):
        '''
        检查租户管理员权限
        '''
        if user.is_superuser:
            return True
        else:
            systempermission = SystemPermission.valid_objects.filter(tenant=tenant, code=tenant.admin_perm_code, is_system=True).first()
            if systempermission:
                userpermissionresult = UserPermissionResult.valid_objects.filter(
                    user=user,
                    tenant=tenant,
                    app=None,
                ).first()
                if userpermissionresult:
                    compress = Compress()
                    permission_result = compress.decrypt(userpermissionresult.result)
                    permission_result_arr = list(permission_result)
                    check_result = int(permission_result_arr[systempermission.sort_id])
                    if check_result == 1:
                        return True
        return False
    
    def create_tenant_admin_permission(self, tenant):
        '''
        创建租户管理员权限
        '''
        systempermission, is_create = SystemPermission.objects.get_or_create(
            tenant=tenant,
            code=tenant.admin_perm_code,
            is_system=True,
        )
        systempermission.name = tenant.name+' manage'
        systempermission.category = 'other'
        systempermission.is_update = True
        systempermission.save()
        return systempermission, is_create
    
    def create_tenant_user_admin_permission(self, tenant, user):
        '''
        创建租户管理员权限和租户管理员
        '''
        systempermission, is_create = self.create_tenant_admin_permission(tenant)
        # if is_create:
        self.add_system_permission_to_user(tenant.id, user.id, systempermission.id)

    def get_user_group_all_permissions(self, tenant_id, user_group_id):
        '''
        获取所有权限并附带是否已授权给用户分组状态
        '''
        usergroup = UserGroup.valid_objects.filter(id=user_group_id).first()
        permission = usergroup.permission
        permission_id = None
        if permission:
            permission_id = permission.id.hex
        # 用户分组
        systempermissions = SystemPermission.valid_objects.filter(
            Q(tenant__isnull=True)|Q(tenant_id=tenant_id)
        )
        for systempermission in systempermissions:
            if systempermission.id.hex == permission_id:
                systempermission.in_current = True
            else:
                systempermission.in_current = False
        return systempermissions

    def check_app_entry_permission(self, request, type, kwargs):
        '''
        检查应用入口权限
        '''
        token = request.GET.get('token', '')
        app_id = None
        if 'app_id' in kwargs:
            app_id = kwargs.get('app_id', None)
        tenant = request.tenant
        if not tenant:
            return False, '没有找到租户'
        tenant_id = tenant.id.hex
        client_id = request.GET.get('client_id', '')

        user = self.token_check(tenant_id, token, request)
        if not user:
            return False, '没有找到用户'

        # 特殊处理 arkid_saas
        app = Application.objects.filter(name='arkid_saas', client_id=client_id).first()
        if app:
            return True, ''

        app = App.valid_objects.filter(
            id=app_id,
            type__in=type
        ).first()
        if not app:
            return False, '没有找到应用'

        permission = app.entry_permission
        if not permission:
            return False, '没有找到入口权限'

        result = self.permission_check_by_sortid(permission, user, app, tenant_id)
        if not result:
            return False, '没有获得授权使用'

        return True, ''
    
    def id_token_reverse(self, id_token):
        '''
        id token转换
        '''
        try:
            payload = jwt.decode(id_token, options={"verify_signature": False})
            return payload
        except Exception:
            raise Exception("unable to parse id_token")
    
    def id_token_to_permission_str(self, request, is_64=False):
        id_token = request.META.get('HTTP_ID_TOKEN', '')
        payload = self.id_token_reverse(id_token)
        client_id = payload.get('aud', None)
        user_id = payload.get('sub_id', '')
        tenant_id = payload.get('tenant_id', '')
    
        apps = App.valid_objects.filter(
            type__in=['OIDC-Platform'],
        )
        app_temp = None
        for app in apps:
            data = app.config.config
            app_client_id = data.get('client_id', '')
            if app_client_id == client_id:
                app_temp = app
                break
        user = User.valid_objects.filter(id=user_id).first()
        if user and app_temp and tenant_id:
            return self.get_permission_str(user, tenant_id, app_temp.id, is_64)
        else:
            print('不存在用户或者应用或者租户')
            return {'result': ''}
    
    def permission_check_by_sortid(self, permission, user, app, tenant_id):
        '''
        根据权限检查用户身份
        '''
        sort_id = permission.sort_id
        userpermissionresult = UserPermissionResult.valid_objects.filter(
            user=user,
            tenant_id=tenant_id,
            app=None,
        ).first()
        if userpermissionresult:
            compress = Compress()
            permission_result = compress.decrypt(userpermissionresult.result)
            permission_result_arr = list(permission_result)
            check_result = int(permission_result_arr[sort_id])
            if check_result == 1:
                return True
        return False

    def token_check(self, tenant_id, token, request):
        '''
        token检查
        '''
        try:
            tenant = Tenant.valid_objects.filter(id=tenant_id).first()
            token = ExpiringToken.objects.get(token=token)
            if token:
                if not token.user.is_active:
                    return None
                if token.expired(tenant=tenant):
                    return None
                user = token.user
                request.user = user
                request.user.tenant = tenant
                request.tenant = tenant
                return user
            return None
        except Exception as e:
            return None
    
    def get_open_appids(self):
        '''
        获取开放的应用id
        '''
        pass
        # permissions = SystemPermission.valid_objects.filter(
        #     is_open=True
        # )
        # app_ids = []
        # for permission in permissions:
        #     app_id = permission.app_id
        #     if app_id not in app_ids:
        #         app_ids.append(app_id)
        # return app_ids

    def get_default_system_permission(self, is_include_self=True):
        '''
        获取默认的系统权限
        '''
        systempermission = SystemPermission.valid_objects.filter(
            name='normal-user',
            category='group',
        ).first()
        if systempermission:
            describe = systempermission.describe
            sort_ids = describe.get('sort_ids', [])
            if is_include_self:
                sort_ids.append(systempermission.sort_id)
            sort_ids.sort()
            return sort_ids
        else:
            return []     

    def get_user_system_permission_arr(self, auth_users, tenant):
        '''
        获取用户的系统权限
        '''
        # 取得当前用户权限数据
        userpermissionresults = UserPermissionResult.valid_objects.filter(
            user__in=auth_users,
            tenant=tenant,
            app=None,
        )
        compress = Compress()
        list_user = []
        for userpermissionresult in userpermissionresults:
            temp_user = userpermissionresult.user
            if userpermissionresult:
                permission_result = compress.decrypt(userpermissionresult.result)
                permission_result_arr = list(permission_result)
                temp_user.arr = permission_result_arr
            else:
                temp_user.arr = []
            list_user.append(temp_user)
        return list_user
    
    def get_child_mans(self, auth_users, tenant):
        '''
        获取子管理员
        '''
        sort_ids = self.get_default_system_permission()
        list_user = self.get_user_system_permission_arr(auth_users, tenant)
        include_id = []
        for item_user in list_user:
            user_arr = item_user.arr
            for index, user_arr_item in enumerate(user_arr):
                if index not in sort_ids and user_arr_item == '1':
                    include_id.append(item_user.id)
                    break
        auth_users = auth_users.filter(id__in=include_id)
        # 区分出那些人是管理员
        systempermission = SystemPermission.valid_objects.filter(tenant=tenant, code=tenant.admin_perm_code, is_system=True).first()
        # 管理权限在arkidpermission表里
        system_userpermissionresults = UserPermissionResult.valid_objects.filter(
            user__in=auth_users,
            tenant=tenant,
            app=None,
        )
        system_userpermissionresults_dict = {}
        for system_userpermissionresult in system_userpermissionresults:
            system_userpermissionresults_dict[system_userpermissionresult.user.id.hex] = system_userpermissionresult
        ids = []
        compress = Compress()
        for auth_user in auth_users:
            # 权限鉴定
            if auth_user.is_superuser:
                auth_user.is_tenant_admin = True
            else:
                if auth_user.id.hex in system_userpermissionresults_dict:
                    system_userpermissionresults_obj = system_userpermissionresults_dict.get(auth_user.id.hex)
                    auth_user_permission_result = compress.decrypt(system_userpermissionresults_obj.result)

                    auth_user_permission_result_arr = list(auth_user_permission_result)
                    check_result = int(auth_user_permission_result_arr[systempermission.sort_id])

                    if check_result == 1:
                        auth_user.is_tenant_admin = True
                    else:
                        ids.append(auth_user.id)
                        auth_user.is_tenant_admin = False
                else:
                    ids.append(auth_user.id)
                    auth_user.is_tenant_admin = False

        if ids:
            return User.valid_objects.filter(id__in=ids)
        else:
            return []

    
    def delete_child_man(self, user, tenant):
        '''
        删除子管理员
        '''
        sort_ids = self.get_default_system_permission()
        # 取得结果字符串
        max_sort_id = SystemPermission.valid_objects.order_by('-sort_id').first().sort_id
        permission_result = ''
        for index in range(0,max_sort_id+1):
            item = 0
            if index in sort_ids:
                item = 1
            permission_result = permission_result + str(item)
        compress = Compress()
        compress_str_result = compress.encrypt(permission_result)
        # 将结果字符串写回去
        userpermissionresult, is_create = UserPermissionResult.objects.get_or_create(
            is_del=False,
            user=user,
            tenant=tenant,
            app=None,
        )
        userpermissionresult.is_update = True
        userpermissionresult.result = compress_str_result
        userpermissionresult.save()
        return True


    def update_close_system_permission_user(self, system_permissions_info):
        '''
        关闭系统权限时会关闭所有授权的租户的用户系统权限
        '''
        tenant_obj = {
        }
        upr = UserPermissionResult.valid_objects.filter(app=None)
        max_sort_id = 0
        for system_permissions_item in system_permissions_info:
            sort_id = system_permissions_item.get('sort_id')
            tenant_id = system_permissions_item.get('tenant_id')
            tenant_items = tenant_obj.get(tenant_id, [])
            tenant_items.append(sort_id)
            tenant_obj[tenant_id] = tenant_items
            if sort_id > max_sort_id:
                max_sort_id = sort_id
        compress = Compress()
        for tenant_id in tenant_obj.keys():
            tenant_sort_ids = tenant_obj.get(tenant_id)
            temp_uprs = upr.exclude(tenant_id=tenant_id)
            for temp_upr in temp_uprs:
                permission_result = compress.decrypt(temp_upr.result)
                permission_result_arr = list(permission_result)
                last_len = max_sort_id+1
                # 补0
                if len(permission_result_arr) < last_len:
                    diff = last_len - len(permission_result_arr)
                    for i in range(diff):
                        permission_result_arr.append(0)
                for sort_id in tenant_sort_ids:
                    permission_result_arr[sort_id] = 0
                permission_result = "".join(map(str, permission_result_arr))
                compress_str_result = compress.encrypt(permission_result)
                temp_upr.result = compress_str_result
                temp_upr.save()


    def update_close_app_permission_user(self, app_permissions_info):
        '''
        关闭应用权限时会关闭所有授权的租户的用户应用权限
        '''
        app_obj = {
        }
        upr = UserPermissionResult.valid_objects.filter(app__isnull=False)
        for app_permissions_item in app_permissions_info:
            app_id = app_permissions_item.get('app_id')
            sort_id = app_permissions_item.get('sort_id')
            tenant_id = app_permissions_item.get('tenant_id')
            if app_id not in app_obj:
                app_obj[app_id] = {
                    'tenant_id': tenant_id,
                    'sort_ids': [sort_id]
                }
            else:
                item = app_obj.get(app_id)
                sort_ids = item.get('sort_ids')
                sort_ids.append(sort_id)
                app_obj[app_id] = item
        # 处理数据
        compress = Compress()
        for app_id in app_obj:
            app_item = app_obj.get(app_id)
            tenant_id = app_item.get('tenant_id')
            sort_ids = app_item.get('sort_ids')
            max_sort_id = 0
            for sort_id in sort_ids:
                if sort_id > max_sort_id:
                    max_sort_id = sort_id
            temp_uprs = upr.exclude(tenant_id=tenant_id).filter(app_id=app_id)
            for temp_upr in temp_uprs:
                permission_result = compress.decrypt(temp_upr.result)
                permission_result_arr = list(permission_result)
                last_len = max_sort_id+1
                # 补0
                if len(permission_result_arr) < last_len:
                    diff = last_len - len(permission_result_arr)
                    for i in range(diff):
                        permission_result_arr.append(0)
                for sort_id in sort_ids:
                    permission_result_arr[sort_id] = 0
                permission_result = "".join(map(str, permission_result_arr))
                compress_str_result = compress.encrypt(permission_result)
                temp_upr.result = compress_str_result
                temp_upr.save()


    def update_open_system_permission_admin(self):
        '''
        给所有admin更新已经开放的系统权限
        '''
        permissions = SystemPermission.valid_objects.filter(is_open=True)
        userinfos = self.get_all_tenant_manager()
        sort_ids = []
        max_sort_id = 0
        for permission in permissions:
            sort_id = permission.sort_id
            sort_ids.append(sort_id)
            if sort_id > max_sort_id:
                max_sort_id = sort_id
        for userinfo in userinfos:
            info_user = userinfo.get('user')
            tenant = userinfo.get('tenant')
            userpermissionresult = UserPermissionResult.valid_objects.filter(
                user=info_user,
                tenant=tenant,
                app=None
            ).first()
            compress = Compress()
            if userpermissionresult:
                user_result_str = compress.decrypt(userpermissionresult.result)
                permission_result_arr = list(user_result_str)
                last_len = max_sort_id+1
                if len(permission_result_arr) < last_len:
                    diff = last_len - len(permission_result_arr)
                    for i in range(diff):
                        permission_result_arr.append(0)
                for sort_id in sort_ids:
                    permission_result_arr[sort_id] = 1
                permission_result = "".join(map(str, permission_result_arr))
                compress_str_result = compress.encrypt(permission_result)
                userpermissionresult.result = compress_str_result
                userpermissionresult.save()


    def update_open_app_permission_admin(self):
        '''
        给所有admin更新已经开放的应用权限
        '''
        open_permission = {
        }
        permissions = Permission.valid_objects.filter(is_open=True)
        for permission in permissions:
            app_id = permission.app_id
            tenant_id = permission.tenant_id
            if app_id not in open_permission:
                open_permission[app_id] = {
                    'app': permission.app,
                    'tenant': permission.tenant,
                    'perms': [permission],
                    'sort_ids': [permission.sort_id]
                }
            else:
                item = open_permission.get(app_id)
                perms = item.get('perms')
                sort_ids = item.get('sort_ids')
                perms.append(permission)
                sort_ids.append(permission.sort_id)
                item['perms'] = perms
                item['sort_ids'] = sort_ids
                open_permission[app_id] = item
        # apps = App.valid_objects.filter(id__in=open_permission.keys())
        userinfos = self.get_all_tenant_manager()
        for key in open_permission.keys():
            item = open_permission.get(key)
            self.update_app_open_permission(item, userinfos)


    def update_app_open_permission(self, item, userinfos):
        '''
        更新某一个应用权限公开权限
        '''
        app_tenant = item.get('tenant')
        app_perms = item.get('perms')
        sort_ids = item.get('sort_ids')
        app = item.get('app')
        max_permission = Permission.objects.filter(app=app).order_by('-sort_id').first()
        admin_users = []
        super_users = []
        for userinfo in userinfos:
            is_super_user = userinfo.get('is_super_user')
            info_tenant = userinfo.get('tenant')
            info_user = userinfo.get('user')
            info_user.tenant = info_tenant
            if is_super_user:
                if info_user not in super_users:
                    super_users.append(info_user)
            else:
                if info_tenant != app_tenant:
                    admin_users.append(info_user)
        # 取得权限字符串
        if max_permission:
            admin_str = ''
            super_user_str = ''
            compress = Compress()
            for i in range(max_permission.sort_id+1):
                super_user_str = super_user_str + '1'
                if i in sort_ids:
                    admin_str = admin_str+'1'
                else:
                    admin_str = admin_str+'0'
            admin_compress_str = compress.encrypt(admin_str)
            super_user_compress_str = compress.encrypt(super_user_str)
            # 更新租户管理员和超级管理员字符串
            for admin_user in admin_users:
                userpermissionresult, is_create = UserPermissionResult.objects.get_or_create(
                    is_del=False,
                    user=admin_user,
                    tenant=admin_user.tenant,
                    app=app,
                )
                userpermissionresult.is_update = True
                userpermissionresult.result = admin_compress_str
                userpermissionresult.save()
            for super_user in super_users:
                userpermissionresult, is_create = UserPermissionResult.objects.get_or_create(
                    is_del=False,
                    user=super_user,
                    tenant=super_user.tenant,
                    app=app,
                )
                userpermissionresult.is_update = True
                userpermissionresult.result = super_user_compress_str
                userpermissionresult.save()


    def update_tenant_use_app_by_user(self, tenant_id, user_id):
        '''
        给某个租户指定用户更新正在使用的应用
        '''
        tenant_uid = uuid.UUID(tenant_id)
        app_infos = self.get_all_user_app(tenant_id)
        user = User.valid_objects.filter(id=user_id).first()
        for app_info in app_infos:
            app_id = app_info.get('app_id')
            app_tenant_id = app_info.get('app_tenant_id')
            if app_tenant_id == tenant_uid:
                # 同一个租户
                self.update_single_user_app_permission(tenant_uid, user_id, app_id)
            else:
                # 不同租户
                max_permission = Permission.objects.filter(app=app_id).order_by('-sort_id').first()
                compress = Compress()
                user_str = ''
                for i in range(max_permission.sort_id+1):
                    user_str = user_str+'0'
                userpermissionresult, is_create = UserPermissionResult.objects.get_or_create(
                    is_del=False,
                    user_id=user_id,
                    tenant_id=tenant_id,
                    app_id=app_id,
                )
                userpermissionresult.is_update = True
                userpermissionresult.result = compress.encrypt(user_str)
                userpermissionresult.save()


    def get_all_tenant_manager(self):
        '''
        取得所有租户管理员(可能会有重复，因为同一个用户会有多个租户)
        '''
        systempermissions = SystemPermission.valid_objects.filter(category='other', is_system=True, code__icontains='tenant_admin')
        userpermissionresults = UserPermissionResult.valid_objects.filter(app=None)
        sort_ids = []
        userinfos = []
        for system_permission in systempermissions:
            sort_id = system_permission.sort_id
            sort_ids.append(sort_id)
        for userpermissionresult in userpermissionresults:
            compress = Compress()
            temp_result = compress.decrypt(userpermissionresult.result)
            temp_result_arr = list(temp_result)
            for sort_id in sort_ids:
                if len(temp_result_arr) > sort_id:
                    check_result = int(temp_result_arr[sort_id])
                    if check_result == 1:
                        userinfos.append({
                            'tenant': userpermissionresult.tenant,
                            'user': userpermissionresult.user,
                            'is_super_user': userpermissionresult.user.is_superuser
                        })
        return userinfos
        
        
    def get_all_user_app(self, tenant_id):
        '''
        取得某个租户所有使用的应用
        '''
        uprs = UserPermissionResult.valid_objects.filter(
            tenant_id=tenant_id,
            app__isnull=False
        )
        items = []
        for upr in uprs:
            app_id = upr.app.id
            obj = {
                'app_id': app_id,
                'app_tenant_id': upr.app.tenant.id
            }
            if obj not in items:
                items.append(obj)
        return items
