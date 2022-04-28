from ninja import Schema
from pydantic import Field
from ninja import ModelSchema
from arkid.core.models import App
from arkid.core.api import api
from django.db import transaction
from ninja.pagination import paginate
from arkid.core.error import ErrorCode
from typing import Union, Literal, List
from arkid.core.schema import RootSchema
from django.shortcuts import get_object_or_404
from arkid.core.translation import gettext_default as _
from arkid.extension.models import TenantExtensionConfig
from arkid.core.event import Event, register_event, dispatch_event
from arkid.core.extension.app_protocol import AppProtocolExtension
from arkid.core.event import CREATE_APP, UPDATE_APP, DELETE_APP

import uuid


AppConfigSchemaIn = AppProtocolExtension.create_composite_config_schema('AppConfigSchemaIn')


AppSchemaOut = AppProtocolExtension.create_composite_config_schema('AppSchemaOut')

class AppConfigSchemaOut(Schema):
    app_id: str


class AppListSchemaOut(ModelSchema):

    class Config:
        model = App
        model_fields = ['id', 'name', 'url', 'logo', 'type']


class ConfigSchemaOut(ModelSchema):

    class Config:
        model = TenantExtensionConfig
        model_fields = ['config']


# class AppSchemaOut(ModelSchema):

#     config: AppConfigSchemaIn

#     class Config:
#         model = App
#         model_fields = ['id', 'name', 'url', 'logo', 'description', 'type', 'config']


@transaction.atomic
@api.post("/{tenant_id}/apps", response=AppConfigSchemaOut, tags=['应用'], auth=None)
def create_app(request, tenant_id: str, data: AppConfigSchemaIn):
    '''
    app创建
    '''
    data.id = uuid.uuid4()
    tenant = request.tenant
    # 事件分发
    results = dispatch_event(Event(tag=CREATE_APP, tenant=tenant, request=request, data=data))
    for func, (result, extension) in results:
        if result:
            # 创建config
            config = extension.create_tenant_config(tenant, data.config.dict())
            # 创建app
            app = App()
            app.id = data.id
            app.name = data.name
            app.url = data.url
            app.logo = data.logo
            app.type = data.app_type
            app.package = data.package
            app.description = data.description
            app.config = config
            app.tenant_id = tenant_id
            app.save()
            break
    return {"app_id": app.id.hex}

@api.get("/{tenant_id}/apps", response=List[AppListSchemaOut], tags=['应用'], auth=None)
@paginate
def list_apps(request, tenant_id: str):
    '''
    app列表
    '''
    apps = App.valid_objects.filter(
        tenant_id=tenant_id
    )
    return apps

@api.get("/{tenant_id}/apps/{app_id}", response=AppSchemaOut, tags=['应用'], auth=None)
def get_app(request, tenant_id: str, app_id: str):
    '''
    获取app
    '''
    app = get_object_or_404(App, id=app_id, is_del=False)
    result = {
        'id': app.id,
        'name': app.name,
        'url': app.url,
        'logo': app.logo,
        'description': app.description,
        'type': app.type,
        'app_type': app.type,
        'package': app.package,
        'config': app.config.config
    }
    return result

@api.delete("/{tenant_id}/apps/{app_id}", tags=['应用'])
def delete_app(request, tenant_id: str, app_id: str):
    '''
    删除app
    '''
    tenant = request.tenant
    app = get_object_or_404(App, id=app_id, is_del=False)
    # 分发事件开始
    app.app_type = app.type
    dispatch_event(Event(tag=DELETE_APP, tenant=tenant, request=request, data=app))
    # 分发事件结束
    app.delete()
    return {'error': ErrorCode.OK.value}

@api.put("/{tenant_id}/apps/{app_id}", tags=['应用'], auth=None)
def update_app(request, tenant_id: str, app_id: str, data: AppConfigSchemaIn):
    '''
    修改app
    '''
    # data = data_1.__root__
    tenant = request.tenant
    # 分发事件开始
    results = dispatch_event(Event(tag=UPDATE_APP, tenant=tenant, request=request, data=data))
    for func, (result, extension) in results:
        # 修改app信息
        app = get_object_or_404(App, id=app_id, is_del=False)
        app.name = data.name
        app.url = data.url
        app.logo = data.logo
        app.type = data.app_type
        app.package = data.package
        app.description = data.description
        # app.config = config
        # app.tenant_id = tenant_id
        app.save()
        # 修改config
        extension.update_tenant_config(app.config.id, data.config.dict())
        break
    return {'error': ErrorCode.OK.value}
