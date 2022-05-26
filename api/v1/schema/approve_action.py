#!/usr/bin/env python3

from typing import List
from pydantic import Field
from ninja import Schema, ModelSchema
from arkid.core.translation import gettext_default as _
from arkid.core.extension.external_idp import ExternalIdpExtension
from arkid.core.schema import ResponseSchema
from arkid.core.models import ApproveAction
from enum import Enum
from pydantic import UUID4


class ApproveActionListItemOut(ModelSchema):
    class Config:
        model = ApproveAction
        model_fields = ['id', 'name', 'path', 'method', 'description']

    package: str = Field(title=_('Package', '插件包'))

    @staticmethod
    def resolve_package(obj):
        if obj.extension:
            return obj.extension.package
        else:
            return ''


class METHOD_TYPE(str, Enum):
    GET = _('GET', 'GET')
    POST = _('POST', 'POST')
    DELETE = _('DELETE', 'DELETE')
    PUT = _('PUT', 'PUT')


class ApproveActionSchema(Schema):
    name: str = Field(title=_('Name', '名称'), default='')
    description: str = Field(title=_('Description', '备注'), default='')
    path: str = Field(title=_('Path', '请求路径'))
    method: METHOD_TYPE = Field(title=_('Method', '请求方法'))
    extension_id: UUID4 = Field(title=_('Extension Id', '插件ID'))


class ApproveActionListOut(ResponseSchema):
    data: List[ApproveActionListItemOut]


class ApproveActionOut(ResponseSchema):
    data: ApproveActionSchema


class ApproveActionCreateIn(ApproveActionSchema):
    pass


class ApproveActionCreateOut(ResponseSchema):
    pass


class ApproveActionUpdateIn(ApproveActionSchema):
    pass


class ApproveActionUpdateOut(ResponseSchema):
    pass


class ApproveActionDeleteOut(ResponseSchema):
    pass
