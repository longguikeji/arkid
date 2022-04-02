from typing import Dict
from django.dispatch import Signal
from django.utils.translation import gettext_lazy as _


class TagSignal:

    def __init__(self, tag, name, data_model=None, description='') -> None:
        self.signal = Signal()
        self.tag = tag
        self.name = name
        self.data_model = data_model
        self.description = description


class Event:

    def __init__(self, tag, tenant, data) -> None:
        self.tag = tag
        self.tenant = tenant
        self.data = data


tag_map_signal: Dict[str, Event] = {}
temp_listens:list = []


def register(tag, name, data_model=None, description=''):
    tag_map_signal[tag] = TagSignal(tag=tag, name=name, data_model=data_model, description=description)


def register_signal(tag_signal: TagSignal):
    tag_map_signal[tag_signal.tag] = tag_signal


def unregister(tag):
    tag_map_signal.pop(tag, None)


def dispatch(event, sender=None):
    if len(temp_listens) > 0:
        for tag,func,kwargs in temp_listens:
            listen_event(tag,func,**kwargs)
        temp_listens.clear()
    tag_signal = tag_map_signal.get(event.tag)
    if not tag_signal:
        return
    if tag_signal.data_model:
        event.data = tag_signal.data_model(**event.data)
    return tag_signal.signal.send(sender=sender, event=event)


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
                tag_signal = tag_map_signal.get(t)
                if tag_signal:
                    tag_signal.signal.connect(signal_func, **kwargs)
        else:
            tag_signal = tag_map_signal.get(tag)
            if tag_signal:
                tag_signal.signal.connect(signal_func, **kwargs)
        return func

    return _decorator


def listen_event(tag, func, **kwargs):

    if isinstance(tag, (list, tuple)):
        for t in tag:
            tag_signal = tag_map_signal.get(t)
            if tag_signal:
                tag_signal.signal.connect(func, **kwargs)
    else:
        tag_signal = tag_map_signal.get(tag)
        if tag_signal:
            tag_signal.signal.connect(func, **kwargs)
        else:
            temp_listens.append((tag,func, kwargs))

def unlisten_event(tag, func, **kwargs):
    if isinstance(tag, (list, tuple)):
        for t in tag:
            tag_signal = tag_map_signal.get(t)
            if tag_signal:
                tag_signal.signal.disconnect(func, **kwargs)
    else:
        tag_signal = tag_map_signal.get(tag)
        if tag_signal:
            tag_signal.signal.disconnect(func, **kwargs)


SEND_SMS_CODE = 'SEND_SMS_CODE'

from pydantic import BaseModel

class SendSMSCodeDataModel(BaseModel):
    code: str

register(tag=SEND_SMS_CODE, name=_('发送短信验证码'), data_model=SendSMSCodeDataModel)
