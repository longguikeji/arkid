from arkid.core import event as core_event
from arkid.tasks.tasks import update_permission


class EventCall(object):
    '''
    处理事件回调
    '''
    def __init__(self):
        core_event.listen_event('api_v1_views_auth_auth', self.login)

    def login(self, event, **kwargs):
        update_permission.delay()

EventCall()