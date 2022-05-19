from arkid.core import event as core_event
from arkid.core.models import(
    Permission, SystemPermission,
)
from arkid.core.event import (
    CREATE_GROUP, DELETE_GROUP, CREATE_APP_DONE,
    DELETE_APP, APP_START, USER_REGISTER,
    SET_APP_OPENAPI_VERSION, UPDATE_APP_USER_API_PERMISSION,
    CREATE_GROUP_PERMISSION, DELETE_GROUP_PERMISSION,
    REMOVE_GROUP_PERMISSION_PERMISSION, UPDATE_GROUP_PERMISSION_PERMISSION,
    CREATE_PERMISSION, UPDATE_PERMISSION, DELETE_PERMISSION,
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
        core_event.listen_event(CREATE_APP_DONE, self.create_app)
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
        return True
    
    def create_app(self, event, **kwargs):
        app = event.data
        tenant = event.tenant
        permission = Permission()
        permission.name = app.name
        permission.code = 'entry_{}'.format(uuid.uuid4())
        permission.tenant = tenant
        permission.app = app
        permission.category = 'entry'
        permission.is_system = True
        permission.save()
        return True
    
    def delete_app(self, event, **kwargs):
        app = event.data
        tenant = event.tenant
        Permission.active_objects.filter(category='entry', app=app, is_system=True).delete()
        return True
    
    def create_group_permission(self, event, **kwargs):
        permission = event.data
        tenant = event.tenant
        from arkid.core.tasks.tasks import update_app_permission
        update_app_permission.delay(tenant.id, permission.app.id)
        return True

    def delete_group_permission(self, event, **kwargs):
        permission = event.data
        tenant = event.tenant
        from arkid.core.tasks.tasks import update_app_permission
        update_app_permission.delay(tenant.id, permission.app.id)
        return True

    def remove_group_permission_permission(self, event, **kwargs):
        permission = event.data
        tenant = event.tenant
        from arkid.core.tasks.tasks import update_app_permission
        update_app_permission.delay(tenant.id, permission.app.id)
        return True

    def update_group_permission_permission(self, event, **kwargs):
        permission = event.data
        tenant = event.tenant
        from arkid.core.tasks.tasks import update_app_permission
        update_app_permission.delay(tenant.id, permission.app.id)
        return True

    def create_permission(self, event, **kwargs):
        permission = event.data
        tenant = event.tenant
        from arkid.core.tasks.tasks import update_app_permission
        update_app_permission.delay(tenant.id, permission.app.id)
        return True

    def update_permission(self, event, **kwargs):
        permission = event.data
        tenant = event.tenant
        from arkid.core.tasks.tasks import update_app_permission
        update_app_permission.delay(tenant.id, permission.app.id)
        return True

    def delete_permission(self, event, **kwargs):
        permission = event.data
        tenant = event.tenant
        from arkid.core.tasks.tasks import update_app_permission
        update_app_permission.delay(tenant.id, permission.app.id)
        return True

EventListener()