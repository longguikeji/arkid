from ninja import Schema
from pydantic import Field
from ninja import ModelSchema
from arkid.core.models import App
from arkid.core.api import api, operation
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
from arkid.core.constants import NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN
from arkid.core.event import(
    CREATE_APP, UPDATE_APP, DELETE_APP,
    CREATE_APP_DONE, SET_APP_OPENAPI_VERSION,
)

import uuid

from arkid.core.pagenation import CustomPagination
from api.v1.schema.app import AppCreateIn, AppCreateOut, AppListItemOut, AppListOut, AppOut, AppUpdateIn, AppUpdateOut


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


class ConfigOpenApiVersionSchemaOut(Schema):

    version: str = Field(title=_('version','应用版本'), default='')
    openapi_uris: str = Field(title=_('openapi uris','接口文档地址'), default='')


# class AppSchemaOut(ModelSchema):

#     config: AppConfigSchemaIn

#     class Config:
#         model = App
#         model_fields = ['id', 'name', 'url', 'logo', 'description', 'type', 'config']


@transaction.atomic
@api.post("/tenant/{tenant_id}/apps/", response=AppCreateOut, tags=['应用'], auth=None)
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def create_app(request, tenant_id: str, data: AppCreateIn):
    '''
    app创建
    '''
    # data.id = uuid.uuid4()
    setattr(data,"id",uuid.uuid4())
    tenant = request.tenant
    # 事件分发
    results = dispatch_event(Event(tag=CREATE_APP, tenant=tenant, request=request, data=data))
    for func, (result, extension) in results:
        if result:
            # 创建config
            config = extension.create_tenant_config(tenant, data.config.dict(), data.name, data.app_type)
            # 创建app
            app = App()
            app.id = data.id
            app.name = data.dict()["name"]
            app.url = data.url
            app.logo = data.logo
            app.type = data.app_type
            app.package = data.package
            app.description = data.description
            app.config = config
            app.tenant_id = tenant_id
            app.save()
            # 创建app完成进行事件分发
            dispatch_event(Event(tag=CREATE_APP_DONE, tenant=tenant, request=request, data=app))
            break
    return {'error': ErrorCode.OK.value}

@api.get("/tenant/{tenant_id}/apps/", response=List[AppListItemOut], tags=['应用'], auth=None)
@operation(AppListOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(CustomPagination)
def list_apps(request, tenant_id: str):
    '''
    app列表
    '''
    apps = App.valid_objects.filter(
        tenant_id=tenant_id
    )
    return apps

@api.get("/tenant/{tenant_id}/apps/{app_id}/", response=AppOut, tags=['应用'], auth=None)
@operation(AppOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
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
    return {"data":result}

@api.get("/tenant/{tenant_id}/apps/{app_id}/openapi_version/", response=ConfigOpenApiVersionSchemaOut, tags=['应用'], auth=None)
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def get_app_openapi_version(request, tenant_id: str, app_id: str):
    '''
    获取app的openapi地址和版本
    '''
    app = get_object_or_404(App, id=app_id, is_del=False)
    app_config = app.config.config
    result = {
        'version': app_config.get('version', ''),
        'openapi_uris': app_config.get('openapi_uris', '')
    }
    return result


@api.put("/tenant/{tenant_id}/apps/{app_id}/openapi_version/", tags=['应用'], auth=None)
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def set_app_openapi_version(request, tenant_id: str, app_id: str, data:ConfigOpenApiVersionSchemaOut):
    '''
    获取app的openapi地址和版本
    '''
    app = get_object_or_404(App, id=app_id, is_del=False)
    config = app.config
    app_config = config.config
    if data.version and data.openapi_uris:
        if data.version != app_config['version'] or data.openapi_uris != app_config['openapi_uris']:
            # 只有版本或接口发生变化时才调用事件
            dispatch_event(Event(tag=SET_APP_OPENAPI_VERSION, tenant=request.tenant, request=request, data=app))
        app_config['version'] = data.version
        app_config['openapi_uris'] = data.openapi_uris
    config.save()
    return {'error': ErrorCode.OK.value}

@api.delete("/tenant/{tenant_id}/apps/{app_id}/", tags=['应用'], auth=None)
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
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

@api.put("/tenant/{tenant_id}/apps/{app_id}/", tags=['应用'], auth=None)
@operation(AppUpdateOut,roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def update_app(request, tenant_id: str, app_id: str, data: AppUpdateIn):
    '''
    修改app
    '''
    # data = data_1.__root__
    tenant = request.tenant
    data.id = app_id
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
        extension.update_tenant_config(app.config.id, data.config.dict(), app.name, data.app_type)
        break
    return {'error': ErrorCode.OK.value}

@api.get("/tenant/{tenant_id}/apps/{app_id}/permissions/", tags=["应用"], auth=None)
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def get_app_permissions(request, tenant_id: str,app_id:str):
    """ 应用权限列表,TODO
    """
    return []