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
            tenant = Tenant.valid_objects.filter(tenant_id)
        # 取得当前租户的所有用户
        auth_users = User.valid_objects.filter(tenant__id=tenant.id)
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
        system_permissions = SystemPermission.valid_objects.order_by('sort_id')
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
        auth_users = User.valid_objects.filter(tenant__id=tenant.id)
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
        auth_users = User.valid_objects.filter(tenant__id=tenant.id)
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
    
    def get_permissions_by_search(self, tenant_id, app_id, user_id, group_id):
        '''
        根据应用，用户，分组查权限
        '''
        permissions = Permission.valid_objects.filter(
            Q(tenant_id=tenant_id)|Q(is_open=True)
        )
        systempermissions = SystemPermission.valid_objects.all()

        if app_id:
            systempermissions = systempermissions.filter(id__isnull=True)
            permissions = permissions.filter(app_id=app_id)
        if user_id:
            compress = Compress()
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
                permission_ids = []
                group_permissions = usergroup.permission.all()
                for group_permission in group_permissions:
                    permission_ids.append(group_permission.id)
                if len(permission_ids) == 0:
                    systempermissions = systempermissions.filter(id__isnull=True)
                else:
                    systempermissions = systempermissions.filter(id__in=permission_ids)
                # 没有应用分组，只有系统分组
                permissions = permissions.filter(id__isnull=True)
        return list(permissions)+list(systempermissions)

    def get_permission_str(self, user, tenant_id, app_id, is_64=False):
        '''
        获取权限字符串
        '''
        compress = Compress()
        userpermissionresults = UserPermissionResult.valid_objects.filter(
            user=user,
            tenant_id=tenant_id,
            app=app_id,
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
        if is_create:
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
        
        # 特殊处理 OIDC-Platform
        if app.type == 'OIDC-Platform':
            return True, ''

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
            tenant_id=tenant_id,
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