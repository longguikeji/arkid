from typing import Dict
from django.dispatch import Signal
from arkid.core.translation import gettext_default as _


event_id_map = {}


class EventType:

    def __init__(self, tag, name, data_model=None, description='') -> None:
        self.signal = Signal()
        self.tag = tag
        self.name = name
        self.data_model = data_model
        self.description = description


class Event:

    def __init__(self, tag, tenant, request=None, response=None, data=None, uuid=None) -> None:
        self.tag = tag
        self.tenant = tenant
        self._request = request
        self._response = response
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


def register_event(tag, name, data_model=None, description=''):
    register_event_type(EventType(tag=tag, name=name, data_model=data_model, description=description))


def register_event_type(event_type: EventType):
    tag = event_type.tag
    tag_map_signal[tag] = event_type
    if tag in temp_listens.keys():
        func, kwargs = temp_listens[tag]
        listen_event(tag,func,**kwargs)
        del temp_listens[tag]
    
    # 将事件声明在OpenAPI的文档中
    # def view_func():
    #     pass
    # api.api.default_router.add_api_operation(
    #     methods = ['event'],
    #     path = tag,
    #     view_func = view_func,
    #     response = event_type.data_model,
    #     operation_id = tag + '_event',
    #     summary = event_type.name,
    #     description = event_type.description,
    #     tags = ['event']
    # )


def unregister_event(tag):
    tag_map_signal.pop(tag, None)


def dispatch_event(event, sender=None):
    event_type = tag_map_signal.get(event.tag)
    if not event_type:
        return
    # if event_type.data_model:
    #     event.data = event_type.data_model(**event.data)
    return event_type.signal.send(sender=sender, event=event)


class EventDisruptionData(Exception):
    pass


def break_event_loop(data):
    raise EventDisruptionData(data)


def register_and_dispatch_event(tag, name, tenant, description='', data_model=None, data=None):
    register_event(tag, name, data_model, description)
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
    def signal_func(event, **kwargs2):
        if event.uuid and event_id_map.get(event.uuid,{}).get(func):
            return event_id_map.get(event.uuid,{}).get(func), listener
        
        res = func(**kwargs2)
        if event.uuid:
            event_id_map[event.uuid] = {func: res}
        return res, listener

    if isinstance(tag, (list, tuple)):
        for t in tag:
            event_type = tag_map_signal.get(t)
            if event_type:
                event_type.signal.connect(signal_func, **kwargs)
            else:
                temp_listens[t] = (signal_func, kwargs)
    else:
        event_type = tag_map_signal.get(tag)
        if event_type:
            event_type.signal.connect(signal_func, **kwargs)
        else:
            temp_listens[tag] = (signal_func, kwargs)


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