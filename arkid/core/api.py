import uuid
import functools
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from pydantic.fields import ModelField
from arkid.core.translation import gettext_default as _
from ninja import NinjaAPI, Schema
from ninja.errors import HttpError
from django.http import HttpRequest
from ninja.security import HttpBearer
from ninja.compatibility import get_headers
from ninja.security.http import HttpAuthBase
from ninja.openapi.schema import OpenAPISchema
from arkid.common.logger import logger
from arkid.core.openapi import get_openapi_schema
from arkid.core.event import register_event, dispatch_event, Event, EventDisruptionData
from arkid.core.models import ExpiringToken, Tenant, App
from arkid.core.token import refresh_token, generate_token

import uuid

def add_fields(cls, **field_definitions: Any):
    new_fields: Dict[str, ModelField] = {}
    new_annotations: Dict[str, Optional[type]] = {}

    for f_name, f_def in field_definitions.items():
        if isinstance(f_def, tuple):
            try:
                f_annotation, f_value = f_def
            except ValueError as e:
                raise Exception(
                    'field definitions should either be a tuple of (<type>, <default>) or just a '
                    'default value, unfortunately this means tuples as '
                    'default values are not allowed'
                ) from e
        else:
            if isinstance(f_def, type):
                f_annotation, f_value = f_def, None
            else:
                f_annotation, f_value = None, f_def
        if f_value is Ellipsis:
            f_value = None

        if f_annotation:
            new_annotations[f_name] = f_annotation

        new_fields[f_name] = ModelField.infer(name=f_name, value=f_value, annotation=f_annotation, class_validators=None, config=cls.__config__)

    cls.__fields__.update(new_fields)
    cls.__annotations__.update(new_annotations)
    cls.__schema_cache__.clear()
		
	
def remove_fields(cls, fields: Any):
    if isinstance(fields, list) or  isinstance(fields, tuple):
        for field in fields:
            cls.__fields__.pop(field, None)
            cls.__annotations__.pop(field, None)
    else:
        cls.__fields__.pop(fields)
        cls.__annotations__.pop(fields, None)
    cls.__schema_cache__.clear()


# from pydantic import BaseModel
# class Model(BaseModel):
#     foo: str

# # add_fields(Model, bar=(str, ...), baz='qwe')
# add_fields(Model, bar=(str), baz='qwe')
# print(Model.schema())
# remove_fields(Model, 'bar')
# print(Model.schema())

class HttpBaseBearer(HttpAuthBase, ABC):
    openapi_scheme: str = "bearer"
    header: str = "Authorization"
    app_id: str = "APP_ID"
    app_secret: str = "APP_SECRET"

    def __call__(self, request: HttpRequest) -> Optional[Any]:
        headers = get_headers(request)
        auth_value = headers.get(self.header, None)
        token = None
        if auth_value:
            parts = auth_value.split(" ")
            if parts[0].lower() == self.openapi_scheme:
                token = " ".join(parts[1:])

        app_id = headers.get(self.app_id, None)
        app_secret = headers.get(self.app_secret, None)

        return self.authenticate(request, token, app_id, app_secret)

    @abstractmethod
    def authenticate(self, request: HttpRequest, token: str, app_id:str, app_secret:str) -> Optional[Any]:
        pass  # pragma: no cover

class GlobalAuth(HttpBaseBearer):
    openapi_scheme = "token"

    def authenticate(self, request, token, app_id, app_secret):
        from arkid.core.models import User  
        try:
            if request.user and isinstance(request.user, User):  # restore 审批请求时，user已经存在，不需要再校验token
                token = ExpiringToken.objects.filter(user=request.user).first()
                if not token:
                    token = ExpiringToken.objects.create(user=request.user, token=generate_token())
                tenant = request.tenant
            else:
                if token:
                    # 使用传统的token访问
                    token = ExpiringToken.objects.get(token=token)
                    if not token.user.is_active:
                        raise HttpError(401, _('User inactive or deleted','用户无效或被删除'))
                    tenant = request.tenant or Tenant.platform_tenant()
                    if token.expired(tenant):
                        raise HttpError(401, _('Token has expired','秘钥已经过期'))
                    # 获取操作id查询用户权限
                    operation_id = request.operation_id
                    if operation_id:
                        from arkid.core.perm.permission_data import PermissionData
                        permissiondata = PermissionData()
                        if token.user and tenant:
                            result = permissiondata.api_system_permission_check(request.tenant, token.user, operation_id)
                            if result is False:
                                raise HttpError(403, _('You do not have api permission','你没有这个接口的权限'))
                    # 将用户信息附加到request中
                    expand_user_dict = User.expand_objects.filter(id=token.user.id).first()
                    request.user = token.user
                    request.user_expand = expand_user_dict
                    return token
                elif app_id and app_secret:
                    try:
                        if uuid.UUID(app_id).version == 4:
                            pass
                    except ValueError:
                        logger.error(_("invalid app_id", "无效的应用id"))
                        return
                    app = App.valid_objects.get(id=app_id, secret=app_secret)
                    tenant = request.tenant or Tenant.platform_tenant()
                    # 获取操作id查询用户权限
                    operation_id = request.operation_id
                    if operation_id and app and tenant:
                        from arkid.core.perm.permission_data import PermissionData
                        permissiondata = PermissionData()
                        result = permissiondata.api_system_permission_check_app(tenant, app, operation_id)
                        if result is False:
                            raise HttpError(403, _('You do not have api permission','你没有这个接口的权限'))
                    request.app = app
                    return app_secret
                else:
                    raise ExpiringToken.DoesNotExist
        except ExpiringToken.DoesNotExist:
            logger.error(_("Invalid token","无效的秘钥"))
            return
        except App.DoesNotExist:
            logger.error(_("invalid app_id app_secret", "无效的应用"))
            return
        # except Exception as err:
        #     logger.error(err)
        #     return


class ArkidApi(NinjaAPI):
    def create_response(self, request, *args, **kwargs):
            response = super().create_response(request, *args, **kwargs)
            if request.META.get('request_id'):
                response.headers['request_id'] = request.META.get('request_id')
            return response


api = ArkidApi(auth=GlobalAuth(),title='ArkID',version='2.5.0')

api.get_openapi_schema = functools.partial(get_openapi_schema, api)


def operation(respnose_model=None, use_id=False, roles: Optional[List[str]] = None, **kwargs):
    from functools import partial

    class ApiEventData(Schema):
        request: Any
        response: respnose_model 

    def replace_view_func(operation):
        tag = api.get_openapi_operation_id(operation)
        register_event(
            tag = tag + '_pre',
            name = operation.summary,
            description = operation.description,
        )
        register_event(
            tag = tag,
            name = operation.summary,
            description = operation.description,
            data_schema = ApiEventData
        )

        old_view_func = operation.view_func
        def func(request, *params, **kwargs):
            request_id = request.META.get('request_id')
            if not request_id and use_id:
                request_id = uuid.uuid4().hex
                request.META['request_id'] = request_id
            
            dispatch_event(Event(tag+'_pre', request.tenant, request=request, uuid=request_id))
            response = old_view_func(request=request, *params, **kwargs)
            # copy request
            dispatch_event(Event(tag, request.tenant, request=request, response=response, uuid=request_id))
            # response 设置 header
            # 前端拿到response header request_id 存储到内存，后续请求都带上request_id header
            # session
            return response
        func.__name__ = old_view_func.__name__
        func.__module__ = old_view_func.__module__
        if roles:
            kwargs.update(roles=roles)
            setattr(func, "arkid_extension", kwargs)
        operation.view_func = func

    def decorator(view_func):
        old_ninja_contribute_to_operation = getattr(view_func, '_ninja_contribute_to_operation', None)
        def ninja_contribute_to_operation(operation):
            if old_ninja_contribute_to_operation:
                old_ninja_contribute_to_operation(operation)
            replace_view_func(operation)
            
        view_func._ninja_contribute_to_operation = partial(
            ninja_contribute_to_operation
        )
        return view_func

    return decorator


@api.exception_handler(EventDisruptionData)
def event_disrupt(request, exc):
    return api.create_response(
        request,
        exc.args[0],
        status=200,
    )