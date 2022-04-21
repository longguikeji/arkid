from ninja import Schema
from typing import Union, Literal, List
from pydantic import Field
from arkid.core import extension
from arkid.core.api import api
from django.db import transaction
from arkid.core.schema import RootSchema
from arkid.core.translation import gettext_default as _
from arkid.extension.models import TenantExtensionConfig, Extension
from arkid.core.event import Event, register_event, dispatch_event
from arkid.core.extension.auth_factor import AuthFactorExtension

AuthFatorSchemaIn = AuthFactorExtension.create_composite_config_schema('AuthFatorSchemaIn')

class AuthFatorSchemaOut(Schema):
    config_id: str

@transaction.atomic
@api.post("/{tenant_id}/auth_fator/", response=AuthFatorSchemaOut, auth=None)
def create_auth_fator(request, tenant_id: str, data: AuthFatorSchemaIn):
    config = TenantExtensionConfig()
    config.tenant = request.tenant
    config.extension = Extension.active_objects.get(package=data.package)
    config.config = data.config.dict()
    config.save()
    return {"config_id": config.id.hex}



class AuthFatorListSchemaOut(Schema):
    # data: List[AuthFatorSchemaIn]
    pass

@api.get("/{tenant_id}/auth_fator/", response=AuthFatorListSchemaOut, auth=None)
def create_auth_fator(request, tenant_id: str):
    extensions = Extension.active_objects.filter(type=AuthFactorExtension.TYPE).all()
    configs = TenantExtensionConfig.active_objects.filter(extension__in=extensions)
    return {"data": configs}