from typing import Dict
from django.dispatch import Signal
from django.forms import model_to_dict
from arkid.core.translation import gettext_default as _
from ninja import Schema
from arkid.core.models import Tenant
from django.http import HttpRequest, HttpResponse
from arkid.common.logger import logger
from django.core.serializers import serialize
from django.db import models
from django.db.models.query import QuerySet
from arkid.common.logger import logger
from arkid.common.utils import data_to_simplenamespace
import json
from types import SimpleNamespace
event_id_map = {}


def send_event_through_webhook(event):

    from arkid.core.tasks.tasks import trigger_webhooks_for_event

    tenant = event.tenant
    payload = get_event_payload(event)
    logger.info(f"Webhook is handling event: {payload}")
    trigger_webhooks_for_event.delay(tenant.id.hex, event.tag, payload)


def get_event_payload(event):
    data = event.data
    if isinstance(data, models.Model):
        data = serialize('json', [data])
    elif type(data) is QuerySet:
        data = serialize('json', data)
    elif isinstance(data, Schema):
        data = data.dict()

    request = None
    response = None

    if event.request and isinstance(event.request, HttpRequest):
        request = {
            "body": str(event.request.body, encoding='utf-8'),
        }

    if event.response and isinstance(event.response, HttpResponse):
        response = {
            "body": str(event.response.body, encoding='utf-8'),
            "status_code": event.response.status_code,
        }
    elif type(event.response) is dict:
        response = event.response
    payload = {
        "tag": event.tag,
        "tenant": event.tenant.id.hex,
        "request": request,
        "response": response,
        "data": data,
        "uuid": event.uuid,
    }
    return json.dumps(payload)

signal_maps = {}

class EventType:
    def __init__(
        self,
        tag: str,
        name: str,
        data_schema: Schema = None,
        result_schema: Schema = None,
        request_schema: Schema = None,
        response_schema: Schema = None,
        description: str = '',
    ):
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
        if tag not in signal_maps:
            signal_maps[tag] = Signal()
        self.tag = tag
        self.name = name
        self.data_schema = data_schema
        self.result_schema = result_schema
        self.request_schema = request_schema
        self.response_schema = response_schema
        self.description = description
        
    @property
    def signal(self):
        return signal_maps[self.tag]


class Event:
    def __init__(
        self,
        tag: str,
        tenant: Tenant = None,
        request: HttpRequest = None,
        response: HttpResponse = None,
        packages: str = None,
        data = None,
        uuid: str = None,
    ):
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
        self.data = data_to_simplenamespace(data)
        self.uuid = uuid

    @property
    def request(self):
        return self._request

    @property
    def response(self):
        return self._response


tag_map_event_type: Dict[str, EventType] = {}
temp_listens: Dict[str, tuple] = {}


def register_event(tag, name, data_schema=None, description=''):
    register_event_type(
        EventType(tag=tag, name=name, data_schema=data_schema, description=description)
    )


def register_event_type(event_type: EventType):
    tag = event_type.tag
    if tag in tag_map_event_type:
        logger.warning(f'重复注册事件：{tag}')
    tag_map_event_type[tag] = event_type
    if tag in temp_listens.keys():
        func, listener, kwargs = temp_listens[tag]
        listen_event(tag, func, listener, **kwargs)
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
    tag_map_event_type.pop(tag, None)


def dispatch_event(event, sender=None):
    # if not event.tenant:
    #     raise Warning("None Tenant!")
    event_type = tag_map_event_type.get(event.tag)
    if not event_type:
        logger.info(f'没有找到{event.tag}对应的事件类型')
        return
    # if event_type.data_schema:
    #     event.data = event_type.data_schema(**event.data)
    try:
        send_event_through_webhook(event)
    except Exception as e:
        logger.error(e)
    logger.info(f'dispatch event: {event.tag}')
    return event_type.signal.send(sender=sender, event=event)


class EventDisruptionData(Exception):
    pass


def break_event_loop(data):
    raise EventDisruptionData(data)


def register_and_dispatch_event(
    tag, name, tenant, description='', data_schema=None, data=None
):
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
                event_type = tag_map_event_type.get(t)
                if event_type:
                    event_type.signal.connect(signal_func, **kwargs)
        else:
            event_type = tag_map_event_type.get(tag)
            if event_type:
                event_type.signal.connect(signal_func, **kwargs)
        return func

    return _decorator


def remove_event_id(event):
    if event.uuid:
        event_id_map.pop(event.uuid, None)


def listen_event(tag, func, listener=None, **kwargs):
    def signal_func(sender, event, **kwargs2):
        if event.uuid and event_id_map.get(event.uuid, {}).get(func):
            return event_id_map.get(event.uuid, {}).get(func), listener

        res = func(sender=sender, event=event, **kwargs2)
        if event.uuid:
            event_id_map[event.uuid] = {func: res}
        return res, listener

    if isinstance(tag, (list, tuple)):
        for t in tag:
            event_type = tag_map_event_type.get(t)
            if event_type:
                event_type.signal.connect(signal_func, **kwargs)
            else:
                temp_listens[t] = (func, listener, kwargs)
    else:
        event_type = tag_map_event_type.get(tag)
        if event_type:
            event_type.signal.connect(signal_func, **kwargs)
        else:
            temp_listens[tag] = (func, listener, kwargs)


def unlisten_event(tag, func, **kwargs):
    if isinstance(tag, (list, tuple)):
        for t in tag:
            event_type = tag_map_event_type.get(t)
            if event_type:
                event_type.signal.disconnect(func, **kwargs)
    else:
        event_type = tag_map_event_type.get(tag)
        if event_type:
            event_type.signal.disconnect(func, **kwargs)


# events
CREATE_LOGIN_PAGE_AUTH_FACTOR = 'CREATE_LOGIN_PAGE_AUTH_FACTOR'
CREATE_LOGIN_PAGE_RULES = 'CREATE_LOGIN_PAGE_RULES'
CREATE_APP_CONFIG = 'CREATE_APP_CONFIG'
CREATE_APP_CONFIG_DONE = 'CREATE_APP_CONFIG_DONE'
UPDATE_APP_CONFIG = 'UPDATE_APP_CONFIG'
DELETE_APP = 'DELETE_APP'
SEND_SMS = 'SEND_SMS'
CREATE_GROUP = 'CREATE_GROUP'
UPDATE_GROUP = 'UPDATE_GROUP'
DELETE_GROUP = 'DELETE_GROUP'
GROUP_ADD_USER = 'GROUP_ADD_USER'
GROUP_REMOVE_USER = 'GROUP_REMOVE_USER'
CREATE_PERMISSION = 'CREATE_PERMISSION'
UPDATE_PERMISSION = 'UPDATE_PERMISSION'
DELETE_PERMISSION = 'DELETE_PERMISSION'
USER_REGISTER = 'USER_REGISTER'
CREATE_SYSTEM_TENANT = 'CREATE_SYSTEM_TENANT'
SET_APP_OPENAPI_VERSION = 'SET_APP_OPENAPI_VERSION'
UPDATE_APP_USER_API_PERMISSION = 'UPDATE_APP_USER_API_PERMISSION'
CREATE_GROUP_PERMISSION = 'CREATE_GROUP_PERMISSION'
UPDATE_GROUP_PERMISSION = 'UPDATE_GROUP_PERMISSION'
DELETE_GROUP_PERMISSION = 'DELETE_GROUP_PERMISSION'
REMOVE_GROUP_PERMISSION_PERMISSION = 'REMOVE_GROUP_PERMISSION_PERMISSION'
UPDATE_GROUP_PERMISSION_PERMISSION = 'UPDATE_GROUP_PERMISSION_PERMISSION'
ADD_USER_SYSTEM_PERMISSION = 'ADD_USER_SYSTEM_PERMISSION'
ADD_USER_APP_PERMISSION = 'ADD_USER_APP_PERMISSION'
REMOVE_USER_SYSTEM_PERMISSION = 'REMOVE_USER_SYSTEM_PERMISSION'
REMOVE_USER_APP_PERMISSION = 'REMOVE_USER_APP_PERMISSION'

CREATE_FRONT_THEME_CONFIG = 'CREATE_FRONT_THEME_CONFIG'
UPDATE_FRONT_THEME_CONFIG = 'UPDATE_FRONT_THEME_CONFIG'
DELETE_FRONT_THEME_CONFIG = 'DELETE_FRONT_THEME_CONFIG'

BEFORE_AUTH = 'BEFORE_AUTH'
AUTH_SUCCESS = 'AUTH_SUCCESS'
AUTH_FAIL = 'AUTH_FAIL'

CREATE_ACCOUNT_LIFE_CONFIG = 'CREATE_ACCOUNT_LIFE_CONFIG'
UPDATE_ACCOUNT_LIFE_CONFIG = 'UPDATE_ACCOUNT_LIFE_CONFIG'
DELETE_ACCOUNT_LIFE_CONFIG = 'DELETE_ACCOUNT_LIFE_CONFIG'

CREATE_APPROVE_SYSTEM_CONFIG = 'CREATE_APPROVE_SYSTEM_CONFIG'
UPDATE_APPROVE_SYSTEM_CONFIG = 'UPDATE_APPROVE_SYSTEM_CONFIG'
DELETE_APPROVE_SYSTEM_CONFIG = 'DELETE_APPROVE_SYSTEM_CONFIG'

CREATE_AUTO_AUTH_CONFIG = 'CREATE_AUTO_AUTH_CONFIG'
UPDATE_AUTO_AUTH_CONFIG = 'UPDATE_AUTO_AUTH_CONFIG'
DELETE_AUTO_AUTH_CONFIG = 'DELETE_AUTO_AUTH_CONFIG'

APP_START = 'APP_START'
AUTO_LOGIN = 'AUTO_LOGIN'

SAVE_FILE = 'SAVE_FILE'

ACCOUNT_LIFE_PERIODIC_TASK = 'ACCOUNT_LIFE_PERIODIC_TASK'
CREATE_APPROVE_REQUEST = 'CREATE_APPROVE_REQUEST'

# register events
register_event(
    CREATE_LOGIN_PAGE_AUTH_FACTOR, _('create login page by auth factor', '认证因素生成登录页面')
)
register_event(CREATE_LOGIN_PAGE_RULES, _('create login page rules', '登录页面生成规则'))
register_event(CREATE_APP_CONFIG, _('create app config', '创建应用协议配置'))
register_event(CREATE_APP_CONFIG_DONE, _('create app config done', '创建应用协议配置完成'))
register_event(UPDATE_APP_CONFIG, _('update app config', '修改应用协议配置'))
register_event(DELETE_APP, _('delete app', '删除应用'))
register_event(CREATE_GROUP, _('create group', '创建分组'))
register_event(UPDATE_GROUP, _('update group', '修改分组'))
register_event(DELETE_GROUP, _('delete group', '删除分组'))
register_event(GROUP_ADD_USER, _('add user group', '添加分组用户'))
register_event(GROUP_REMOVE_USER, _('remove user group', '移除分组用户'))
register_event(APP_START, _('app start', '应用启动'))
register_event(SEND_SMS, _('send sms', '发送短信'))
register_event(CREATE_PERMISSION, _('create permission', '创建权限'))
register_event(UPDATE_PERMISSION, _('update permission', '修改权限'))
register_event(DELETE_PERMISSION, _('delete permission', '删除权限'))
register_event(USER_REGISTER, _('user register', '用户注册'))
register_event(SET_APP_OPENAPI_VERSION, _('set app openapi version', '设置应用接口和版本'))
register_event(
    UPDATE_APP_USER_API_PERMISSION, _('update app user api permission', '更新应用的用户接口权限')
)
register_event(BEFORE_AUTH, _('before_auth', '认证前'))
register_event(AUTH_SUCCESS, _('auth success', '认证成功'))
register_event(AUTH_FAIL, _('auth fail', '认证失败'))
register_event(CREATE_GROUP_PERMISSION, _('create group permission', '创建权限分组'))
register_event(UPDATE_GROUP_PERMISSION, _('update group permission', '修改权限分组'))
register_event(DELETE_GROUP_PERMISSION, _('delete group permission', '删除权限分组'))
register_event(
    REMOVE_GROUP_PERMISSION_PERMISSION,
    _('update group permission permission', '移除权限分组的权限'),
)
register_event(
    UPDATE_GROUP_PERMISSION_PERMISSION,
    _('delete group permission permission', '更改权限分组的权限'),
)
register_event(CREATE_ACCOUNT_LIFE_CONFIG, _('Create Account Life', '添加生命周期'))
register_event(UPDATE_ACCOUNT_LIFE_CONFIG, _('Update Account Life', '更新生命周期'))
register_event(DELETE_ACCOUNT_LIFE_CONFIG, _('Delete Account Life', '删除生命周期'))
register_event(CREATE_APPROVE_SYSTEM_CONFIG, _('Create Approve System', '添加审批系统'))
register_event(UPDATE_APPROVE_SYSTEM_CONFIG, _('Update Approve System', '更新审批系统'))
register_event(DELETE_APPROVE_SYSTEM_CONFIG, _('Delete Approve System', '删除审批系统'))
register_event(ADD_USER_SYSTEM_PERMISSION, _('add user system permission', '添加用户系统权限'))
register_event(ADD_USER_APP_PERMISSION, _('add user app permission', '添加用户应用权限'))
register_event(
    REMOVE_USER_SYSTEM_PERMISSION, _('remove user system permission', '移除用户系统权限')
)
register_event(REMOVE_USER_APP_PERMISSION, _('remove user app permission', '移除用户应用权限'))
register_event(AUTO_LOGIN, _('Auto Login', '开始自动登录'))

register_event(CREATE_AUTO_AUTH_CONFIG, _('Create Auto Auth', '添加自动登录'))
register_event(UPDATE_AUTO_AUTH_CONFIG, _('Update Auto Auth', '更新自动登录'))
register_event(DELETE_AUTO_AUTH_CONFIG, _('Delete Auto Auth', '删除自动登录'))

register_event(SAVE_FILE, _('SAVE FILE', '保存文件'))
register_event(ACCOUNT_LIFE_PERIODIC_TASK, _('ACCOUNT_LIFE_PERIODIC_TASK', '生命周期定时任务'))
register_event(CREATE_APPROVE_REQUEST, _('CREATE_APPROVE_REQUEST', '创建审批请求'))
