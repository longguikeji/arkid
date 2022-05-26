#!/usr/bin/env python3

from typing import List
from pydantic import Field
from ninja import Schema, ModelSchema
from arkid.core.translation import gettext_default as _
from arkid.core.extension.external_idp import ExternalIdpExtension
from arkid.core.schema import ResponseSchema
from arkid.core.models import ApproveRequest


class ApproveRequestListItemOut(ModelSchema):
    class Config:
        model = ApproveRequest
        model_fields = ['id', 'status']

    username: str = Field(title=_('Username', '用户名'))
    path: str = Field(title=_('Path', '请求路径'))
    method: str = Field(title=_('Method', '请求方法'))

    @staticmethod
    def resolve_username(obj):
        return obj.user.username

    @staticmethod
    def resolve_path(obj):
        return obj.action.path

    @staticmethod
    def resolve_method(obj):
        return obj.action.method


class ApproveRequestListOut(ResponseSchema):
    data: List[ApproveRequestListItemOut]
