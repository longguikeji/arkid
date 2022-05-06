from typing import Dict
from django.dispatch import Signal
from arkid.core.translation import gettext_default as _
from ninja import Schema
from arkid.core.models import Tenant
from django.http import HttpRequest, HttpResponse

event_id_map = {}


class EventType:

    def __init__(self, tag: str, name: str, data_schema: Schema = None, result_schema: Schema = None, request_schema: Schema = None, response_schema:  Schema = None, description: str = '') -> None:
        """事件类型用于注册
        注意:
            event request 切勿修改

        Args:
            tag (str): 事件类型唯一标识
            name (str): 事件类型名字
            data_schema (Schema, optional): 输入data的Schema
            result_schema (Schema, optional): 事件处理回调函数 return 结果 Schema
            request_schema (Schema, optional): django http request Schema
            response_schema (Schema, optional): django http response Schema
            description (str, optional): 事件类型描述
        """
        self.signal = Signal()
        self.tag = tag
        self.name = name
        self.data_schema = data_schema
        self.result_schema = result_schema
        self.request_schema = request_schema
        self.response_schema = response_schema
        self.description = description


class Event:

    def __init__(self, tag: str, tenant: Tenant, request: HttpRequest=None, response: HttpResponse=None, packages: str=None, data=None, uuid: str=None) -> None:
        """事件

        Args:
            tag (str): 事件类型唯一标识
            tenant (Tenant): 租户
            request (HttpRequest, optional): django http request
            response (HttpResponse, optional): django http response
            packages (str, optional): 插件package标识
            data (_type_, optional): 事件data
            uuid (str, optional): 事件包含的request_uuid
        """
        self.tag = tag
        self.tenant = tenant
        self._request = request
        self._response = response
        self.packages = packages
        self.data = data
        self.uuid = uuid

    @property
    def request(self):
        return self._request

    @property
    def response(self):
        return self._response


tag_map_signal: Dict[str, Event] = {}
temp_listens:Dict[str, tuple] = {}


def register_event(tag, name, data_schema=None, description=''):
    register_event_type(EventType(tag=tag, name=name, data_schema=data_schema, description=description))


def register_event_type(event_type: EventType):
    tag = event_type.tag
    if tag in tag_map_signal:
        return
    tag_map_signal[tag] = event_type
    if tag in temp_listens.keys():
        func, listener, kwargs = temp_listens[tag]
        listen_event(tag,func,listener,**kwargs)
        del temp_listens[tag]
    
    # 将事件声明在OpenAPI的文档中
    # def view_func():
    #     pass
    # api.api.default_router.add_api_operation(
    #     methods = ['event'],
    #     path = tag,
    #     view_func = view_func,
    #     response = event_type.data_schema,
    #     operation_id = tag + '_event',
    #     summary = event_type.name,
    #     description = event_type.description,
    #     tags = ['event']
    # )


def unregister_event(tag):
    tag_map_signal.pop(tag, None)


def dispatch_event(event, sender=None):
    if not event.tenant:
        raise Exception("None Tenant!")
    event_type = tag_map_signal.get(event.tag)
    if not event_type:
        return
    # if event_type.data_schema:
    #     event.data = event_type.data_schema(**event.data)
    return event_type.signal.send(sender=sender, event=event)


class EventDisruptionData(Exception):
    pass


def break_event_loop(data):
    raise EventDisruptionData(data)


def register_and_dispatch_event(tag, name, tenant, description='', data_schema=None, data=None):
    register_event(tag, name, data_schema, description)
    return dispatch_event(Event(tag, tenant, data))


def decorator_listen_event(tag, **kwargs):

    def _decorator(func):
        def signal_func(event, **kwargs2):
            # 判断租户是否启用该插件
            # tenant
            # 插件名 tag
            # func.__module__ 'extension_root.abc.xx'
            # kwargs2.pop()
            # Extension.
            return func(event=event, **kwargs2)

        if isinstance(tag, (list, tuple)):
            for t in tag:
                event_type = tag_map_signal.get(t)
                if event_type:
                    event_type.signal.connect(signal_func, **kwargs)
        else:
            event_type = tag_map_signal.get(tag)
            if event_type:
                event_type.signal.connect(signal_func, **kwargs)
        return func

    return _decorator


def remove_event_id(event):
    if event.uuid:
        event_id_map.pop(event.uuid, None)


def listen_event(tag, func, listener=None, **kwargs):
    def signal_func(sender, event, **kwargs2):
        if event.uuid and event_id_map.get(event.uuid,{}).get(func):
            return event_id_map.get(event.uuid,{}).get(func), listener
        
        res = func(sender=sender, event=event, **kwargs2)
        if event.uuid:
            event_id_map[event.uuid] = {func: res}
        return res, listener

    if isinstance(tag, (list, tuple)):
        for t in tag:
            event_type = tag_map_signal.get(t)
            if event_type:
                event_type.signal.connect(signal_func, **kwargs)
            else:
                temp_listens[t] = (func, listener, kwargs)
    else:
        event_type = tag_map_signal.get(tag)
        if event_type:
            event_type.signal.connect(signal_func, **kwargs)
        else:
            temp_listens[tag] = (func, listener, kwargs)


def unlisten_event(tag, func, **kwargs):
    if isinstance(tag, (list, tuple)):
        for t in tag:
            event_type = tag_map_signal.get(t)
            if event_type:
                event_type.signal.disconnect(func, **kwargs)
    else:
        event_type = tag_map_signal.get(tag)
        if event_type:
            event_type.signal.disconnect(func, **kwargs)


# events
CREATE_LOGIN_PAGE_AUTH_FACTOR = 'CREATE_LOGIN_PAGE_AUTH_FACTOR'
CREATE_LOGIN_PAGE_RULES = 'CREATE_LOGIN_PAGE_RULES'
CREATE_APP = 'CREATE_APP'
CREATE_APP_DONE = 'CREATE_APP_DONE'
UPDATE_APP = 'UPDATE_APP'
DELETE_APP = 'DELETE_APP'
SEND_SMS = 'SEND_SMS'
CREATE_GROUP = 'CREATE_GROUP'
UPDATE_GROUP = 'UPDATE_GROUP'
DELETE_GROUP = 'DELETE_GROUP'
CREATE_PERMISSION = 'CREATE_PERMISSION'
UPDATE_PERMISSION = 'UPDATE_PERMISSION'
DELETE_PERMISSION = 'DELETE_PERMISSION'


# register events
register_event(CREATE_LOGIN_PAGE_AUTH_FACTOR, _('create login page by auth factor','认证因素生成登录页面'))
register_event(CREATE_LOGIN_PAGE_RULES, _('create login page rules','登录页面生成规则'))
register_event(CREATE_APP, _('create app','创建应用'))
register_event(CREATE_APP_DONE, _('create app done','创建应用完成'))
register_event(UPDATE_APP, _('update app','修改应用'))
register_event(DELETE_APP, _('delete app','删除应用'))
register_event(CREATE_GROUP, _('create group','创建分组'))
register_event(UPDATE_GROUP, _('update group','修改分组'))
register_event(DELETE_GROUP, _('delete group','删除分组'))
register_event(SEND_SMS, _('send sms','发送短信'))
register_event(CREATE_PERMISSION, _('create permission','创建权限'))
register_event(UPDATE_PERMISSION, _('update permission','修改权限'))
register_event(DELETE_PERMISSION, _('delete permission','删除权限'))
