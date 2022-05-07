from arkid.core import event as core_event
from arkid.core.models import(
    Permission, SystemPermission,
)
from arkid.core.event import (
    CREATE_GROUP, DELETE_GROUP, CREATE_APP_DONE,
    DELETE_APP,
)

import uuid

class EventCall(object):
    '''
    处理事件回调
    '''
    def __init__(self):
        core_event.listen_event('api_v1_views_auth_auth', self.login)
        core_event.listen_event(CREATE_GROUP, self.create_group)
        core_event.listen_event(DELETE_GROUP, self.delete_group)
        core_event.listen_event(CREATE_APP_DONE, self.create_app)
        core_event.listen_event(DELETE_APP, self.delete_app)

    def login(self, event, **kwargs):
        pass
        # from arkid.core.tasks.tasks import update_permission
        # update_permission.delay()


    def create_group(self, event, **kwargs):
        group = event.data
        tenant = event.tenant
        # permission = GroupPermission()
        # permission.name = group.name
        # permission.code = 'group_{}'.format(uuid.uuid4())
        # permission.tenant = tenant
        # permission.app = None
        # permission.category = 'group'
        # permission.group = group
        # permission.is_system = True
        # permission.save()
        return True


    def delete_group(self, event, **kwargs):
        group = event.data
        tenant = event.tenant
        GroupPermission.active_objects.filter(category='group', group=group, is_system=True).delete()
        return True
    
    def create_app(self, event, **kwargs):
        app = event.data
        tenant = event.tenant
        # permission = Permission()
        # permission.name = app.name
        # permission.code = 'entry_{}'.format(uuid.uuid4())
        # permission.tenant = tenant
        # permission.app = app
        # permission.category = 'entry'
        # permission.is_system = True
        # permission.save()
        return True
    
    def delete_app(self, event, **kwargs):
        app = event.data
        tenant = event.tenant
        # Permission.active_objects.filter(category='entry', app=app, is_system=True).delete()
        return True

EventCall()