import functools
from typing import Any, Dict, Optional
from pydantic.fields import ModelField
from arkid.core.translation import gettext_default as _
from ninja import NinjaAPI, Schema
from ninja.security import HttpBearer
from arkid.common.logger import logger
from arkid.core.openapi import get_openapi_schema
from arkid.core.event import register_event, dispatch, Event
from arkid.core.models import ExpiringToken


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


class GlobalAuth(HttpBearer):
    openapi_scheme = "token"

    def authenticate(self, request, token):
        try:
            token = ExpiringToken.objects.get(token=token)
            
            if not token.user.is_active:
                raise Exception(_('User inactive or deleted'))

            if token.expired():
                raise Exception(_('Token has expired'))
                
        except ExpiringToken.DoesNotExist:
            logger.error(_("Invalid token"))
            return
        except Exception as err:
            logger.error(err)
            return

        request.user = token.user
        return token


api = NinjaAPI(auth=GlobalAuth())

api.get_openapi_schema = functools.partial(get_openapi_schema, api)


class RequestResponse:
    def __init__(self, request, response) -> None:
        self.request = request
        self._response = response

    @property
    def response(self):
        return self._response


def operation(respnose_model):
    from functools import partial

    class ApiEventData(Schema):
        request: Any
        response: respnose_model 

    def replace_view_func(operation):
        tag = api.get_openapi_operation_id(operation)
        register_event(
            tag = tag,
            name = operation.summary,
            description = operation.description,
            data_model = ApiEventData
        )

        old_view_func = operation.view_func
        def func(request, *params, **kwargs):
            response = old_view_func(request=request, *params, **kwargs)
            # copy request
            dispatch(Event(tag, request.tenant, RequestResponse(request, response)))
            print(response)
            return response
        func.__name__ = old_view_func.__name__
        func.__module__ = old_view_func.__module__
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
