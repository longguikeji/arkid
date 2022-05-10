from arkid.core import event as core_event
from arkid.core.models import(
    Permission, SystemPermission,
)
from arkid.core.event import (
    CREATE_GROUP, DELETE_GROUP, CREATE_APP_DONE,
    DELETE_APP, APP_START,
)

import uuid

class EventListener(object):
    '''
    处理事件回调
    '''
    def __init__(self):
        core_event.listen_event(APP_START, self.app_start)
        core_event.listen_event(CREATE_GROUP, self.create_group)
        core_event.listen_event(DELETE_GROUP, self.delete_group)
        core_event.listen_event(CREATE_APP_DONE, self.create_app)
        core_event.listen_event(DELETE_APP, self.delete_app)

    def app_start(self, event, **kwargs):
        pass
        # from arkid.core.tasks.tasks import update_permission
        # update_permission.delay()


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

EventListener()