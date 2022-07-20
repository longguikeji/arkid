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
from arkid.core import pages, actions
from uuid import UUID

select_path_page = pages.TablePage(select=True, name=_("Select Path", "选择路径"))
select_approve_system_page = pages.TablePage(
    select=True, name=_("Select Approve System", "选择审批系统插件")
)

pages.register_front_pages(select_path_page)
pages.register_front_pages(select_approve_system_page)


select_path_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/path_list/',
        method=actions.FrontActionMethod.GET,
    ),
)
select_approve_system_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/approve_system_extensions/',
        method=actions.FrontActionMethod.GET,
    ),
)


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


class ApproveActionExtensionIn(Schema):
    id: UUID = Field(hidden=True)
    name: str


class ApproveActionSchema(Schema):
    name: str = Field(title=_('Name', '名称'), default='')
    description: str = Field(title=_('Description', '备注'), default='')
    path: str = Field(
        title=_('Path', '请求路径'),
        type="string",
        option_action={
            "path": '/api/v1/tenant/{tenant_id}/path_list/',
            "method": actions.FrontActionMethod.GET.value,
        },
        format="autocomplete",
    )
    method: METHOD_TYPE = Field(title=_('Method', '请求方法'))
    extension: ApproveActionExtensionIn = Field(
        title=_('Extension Id', '审批系统'),
        # field="id",
        page=select_approve_system_page.tag,
        # link="name",
        # type="string",
    )


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
