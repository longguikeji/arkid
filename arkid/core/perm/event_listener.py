from arkid.core import event as core_event
from arkid.core.models import(
    Permission, SystemPermission, App,
)
from arkid.core.event import (
    CREATE_GROUP, DELETE_GROUP, CREATE_APP_CONFIG_DONE,
    DELETE_APP, APP_START, USER_REGISTER,
    SET_APP_OPENAPI_VERSION, UPDATE_APP_USER_API_PERMISSION,
    CREATE_GROUP_PERMISSION, DELETE_GROUP_PERMISSION, GROUP_REMOVE_USER,
    REMOVE_GROUP_PERMISSION_PERMISSION, UPDATE_GROUP_PERMISSION_PERMISSION,
    CREATE_PERMISSION, UPDATE_PERMISSION, DELETE_PERMISSION,
    ADD_USER_SYSTEM_PERMISSION, ADD_USER_APP_PERMISSION, GROUP_ADD_USER,
    REMOVE_USER_SYSTEM_PERMISSION, REMOVE_USER_APP_PERMISSION,
)

import uuid

class EventListener(object):
    '''
    处理事件回调
    '''
    def __init__(self):
        core_event.listen_event(USER_REGISTER, self.register)
        core_event.listen_event(APP_START, self.app_start)
        core_event.listen_event(CREATE_GROUP, self.create_group)
        core_event.listen_event(DELETE_GROUP, self.delete_group)
        core_event.listen_event(GROUP_ADD_USER, self.group_add_user)
        core_event.listen_event(GROUP_REMOVE_USER, self.group_remove_user)
        core_event.listen_event(CREATE_APP_CONFIG_DONE, self.create_app)
        core_event.listen_event(DELETE_APP, self.delete_app)
        core_event.listen_event(SET_APP_OPENAPI_VERSION, self.set_app_openapi_version)
        core_event.listen_event(UPDATE_APP_USER_API_PERMISSION, self.update_app_user_api_permission)
        core_event.listen_event(CREATE_GROUP_PERMISSION, self.create_group_permission)
        core_event.listen_event(DELETE_GROUP_PERMISSION, self.delete_group_permission)
        core_event.listen_event(REMOVE_GROUP_PERMISSION_PERMISSION, self.remove_group_permission_permission)
        core_event.listen_event(UPDATE_GROUP_PERMISSION_PERMISSION, self.update_group_permission_permission)
        core_event.listen_event(CREATE_PERMISSION, self.create_permission)
        core_event.listen_event(UPDATE_PERMISSION, self.update_permission)
        core_event.listen_event(DELETE_PERMISSION, self.delete_permission)
        core_event.listen_event(ADD_USER_SYSTEM_PERMISSION, self.add_user_system_permission)
        core_event.listen_event(ADD_USER_APP_PERMISSION, self.add_user_app_permission)
        core_event.listen_event(REMOVE_USER_SYSTEM_PERMISSION, self.remove_user_system_permission)
        core_event.listen_event(REMOVE_USER_APP_PERMISSION, self.remove_user_app_permission)

    def register(self, event, **kwargs):
        from arkid.core.tasks.tasks import update_single_user_system_permission
        user = event.data
        tenant = event.tenant
        update_single_user_system_permission().delay(tenant.id, user.id)

    def app_start(self, event, **kwargs):
        from arkid.core.tasks.tasks import update_system_permission
        update_system_permission.delay()

    def set_app_openapi_version(self, event, **kwargs):
        from arkid.core.tasks.tasks import update_app_permission
        app = event.data
        tenant = event.tenant
        update_app_permission.delay(tenant.id, app.id)
    
    def update_app_user_api_permission(self, event, **kwargs):
        from arkid.core.tasks.tasks import update_single_user_app_permission
        app = event.data
        # 把用户赋在app上给过来
        user = app.user
        tenant = event.tenant
        update_single_user_app_permission.delay(tenant.id, user.id, app.id)

    def create_group(self, event, **kwargs):
        group = event.data
        tenant = event.tenant
        systempermission = SystemPermission()
        systempermission.name = group.name
        systempermission.code = 'group_{}'.format(uuid.uuid4())
        systempermission.tenant = tenant
        systempermission.category = 'group'
        systempermission.is_system = True
        systempermission.operation_id = ''
        systempermission.describe = {}
        systempermission.save()
        # 同步分组权限
        group.permission = systempermission
        group.save()
        # 需要更新系统的全部用户权限
        from arkid.core.tasks.tasks import update_arkid_all_user_permission
        update_arkid_all_user_permission.delay(tenant.id)
        return True
    
    def delete_group(self, event, **kwargs):
        group = event.data
        tenant = event.tenant
        # 删除
        permission = group.permission
        permission.delete()
        # 分组权限清空
        group.permission = None
        group.save()
        # 需要更新系统的全部用户权限
        from arkid.core.tasks.tasks import update_arkid_all_user_permission
        update_arkid_all_user_permission.delay(tenant.id)
        return True
    
    def group_add_user(self, event, **kwargs):
        from arkid.core.tasks.tasks import update_arkid_all_user_permission
        update_arkid_all_user_permission.delay(tenant.id)
        return True

    def group_remove_user(self, event, **kwargs):
        from arkid.core.tasks.tasks import update_arkid_all_user_permission
        update_arkid_all_user_permission.delay(tenant.id)
        return True

    def create_app(self, event, **kwargs):
        app = event.data
        tenant = event.tenant
        permission = SystemPermission()
        permission.name = app.name
        permission.code = 'entry_{}'.format(uuid.uuid4())
        permission.tenant = tenant
        permission.category = 'entry'
        permission.is_system = True
        permission.save()
        # 把应用增加一个权限
        app.entry_permission = permission
        app.save()
        from arkid.core.tasks.tasks import update_arkid_all_user_permission
        update_arkid_all_user_permission.delay(tenant.id)
        return True
    
    def delete_app(self, event, **kwargs):
        app = event.data
        tenant = event.tenant
        permission = Permission.active_objects.filter(category='entry', app=app, is_system=True).first()
        if permission:
            permission.delete()
            from arkid.core.tasks.tasks import update_only_user_app_permission
            update_only_user_app_permission.delay(tenant.id, permission.app.id)
        return True
    
    def create_group_permission(self, event, **kwargs):
        permission = event.data
        tenant = event.tenant
        from arkid.core.tasks.tasks import update_only_user_app_permission
        update_only_user_app_permission.delay(tenant.id, permission.app.id)
        return True

    def delete_group_permission(self, event, **kwargs):
        permission = event.data
        tenant = event.tenant
        from arkid.core.tasks.tasks import update_only_user_app_permission
        update_only_user_app_permission.delay(tenant.id, permission.app.id)
        return True

    def remove_group_permission_permission(self, event, **kwargs):
        permission = event.data
        tenant = event.tenant
        from arkid.core.tasks.tasks import update_only_user_app_permission
        update_only_user_app_permission.delay(tenant.id, permission.app.id)
        return True

    def update_group_permission_permission(self, event, **kwargs):
        permission = event.data
        tenant = event.tenant
        from arkid.core.tasks.tasks import update_only_user_app_permission
        update_only_user_app_permission.delay(tenant.id, permission.app.id)
        return True

    def create_permission(self, event, **kwargs):
        permission = event.data
        tenant = event.tenant
        from arkid.core.tasks.tasks import update_only_user_app_permission
        update_only_user_app_permission.delay(tenant.id, permission.app.id)
        return True

    def update_permission(self, event, **kwargs):
        permission = event.data
        tenant = event.tenant
        from arkid.core.tasks.tasks import update_only_user_app_permission
        update_only_user_app_permission.delay(tenant.id, permission.app.id)
        return True

    def delete_permission(self, event, **kwargs):
        permission = event.data
        tenant = event.tenant
        from arkid.core.tasks.tasks import update_only_user_app_permission
        update_only_user_app_permission.delay(tenant.id, permission.app.id)
        return True

    def add_user_system_permission(self, event, **kwargs):
        permission = event.data
        tenant = event.tenant
        from arkid.core.tasks.tasks import add_system_permission_to_user, update_single_user_app_permission
        add_system_permission_to_user.delay(tenant.id, permission.user_id, permission.id)
        if permission.category == 'entry' and permission.is_open and permission.tenant != tenant:
            app = App.valid_objects.filter(
                entry_permission=permission
            ).first()
            if app:
                config = app.config
                app_config = config.config
                if app_config.get('version') and app_config.get('openapi_uris'):
                    # 如果给了入口权限，需要同步更新app权限
                    update_single_user_app_permission.delay(tenant.id, permission.user_id, app.id)
        return True

    def add_user_app_permission(self, event, **kwargs):
        permission = event.data
        tenant = event.tenant
        from arkid.core.tasks.tasks import add_app_permission_to_user
        add_app_permission_to_user.delay(tenant.id, permission.app_id, permission.user_id, permission.id)
        return True

    def remove_user_system_permission(self, event, **kwargs):
        permission = event.data
        tenant = event.tenant
        from arkid.core.tasks.tasks import remove_system_permission_to_user
        remove_system_permission_to_user.delay(tenant.id, permission.user_id, permission.id)
        return True

    def remove_user_app_permission(self, event, **kwargs):
        permission = event.data
        tenant = event.tenant
        from arkid.core.tasks.tasks import remove_app_permission_to_user
        remove_app_permission_to_user.delay(tenant.id, permission.app_id, permission.user_id, permission.id)
        return True

EventListener()