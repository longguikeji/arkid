from typing import Optional
from ninja import Schema, ModelSchema
from arkid.core.models import Tenant
from arkid.core.translation import gettext_default as _
from arkid.core.schema import ResponseSchema, UserSchemaOut


class AuthIn(Schema):
    username: Optional[str]


class AuthTenantSchema(ModelSchema):
    class Config:
        model = Tenant
        model_fields = ['id', 'name', 'slug', 'icon']
        # validate = False


class AuthDataOut(Schema):
    user: UserSchemaOut
    token: str


class AuthOut(ResponseSchema):
    data: AuthDataOut