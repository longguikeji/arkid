#!/usr/bin/env python3

from abc import abstractmethod
from arkid.core.extension import Extension
from arkid.core.translation import gettext_default as _
from arkid.core import event as core_event
from arkid.extension.models import TenantExtensionConfig
from pydantic import Field
from ninja import Schema
from arkid.core.constants import *
from arkid.core.api import api, operation
from arkid.core.models import ApproveRequest
from arkid.core.error import ErrorCode, ErrorDict
from arkid.core.schema import ResponseSchema


class ApproveRequestOut(ResponseSchema):
    pass


class ApproveSystemBaseSchema(Schema):
    pass_request_url: str = Field(
        default='',
        title=_('Pass Approve Request Url', '通过审批请求URL'),
        readonly=True,
    )
    deny_request_url: str = Field(
        default='',
        title=_('Deny Approve Request Url', '拒绝审批请求URL'),
        readonly=True,
    )


class ApproveSystemExtension(Extension):

    TYPE = "approve_system"

    composite_schema_map = {}
    created_composite_schema_list = []
    composite_key = 'type'
    composite_model = TenantExtensionConfig

    @property
    def type(self):
        return ApproveSystemExtension.TYPE

    def load(self):
        self.listen_event(
            core_event.CREATE_APPROVE_REQUEST, self.create_approve_request
        )
        self.pass_path = self.register_api(
            f'/approve_requests/{{request_id}}/pass/',
            'PUT',
            self.pass_approve_request_handler,
            response=ApproveRequestOut,
        )
        self.deny_path = self.register_api(
            f'/approve_requests/{{request_id}}/deny/',
            'PUT',
            self.deny_approve_request_handler,
            response=ApproveRequestOut,
        )
        super().load()

    @abstractmethod
    def create_approve_request(self, event, **kwargs):
        """
        抽象方法
        Args:
            event (arkid.core.event.Event): 创建审批请求事件
        """
        pass

    @operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
    def pass_approve_request_handler(self, request, request_id):
        approve_request = ApproveRequest.valid_objects.get(id=request_id)
        self.pass_approve_request(request, approve_request)
        approve_request.status = 'pass'
        approve_request.save()
        return ErrorDict(ErrorCode.OK)

    @abstractmethod
    def pass_approve_request(self, request, approve_request):
        """
        抽象方法
        Args:
            request (django.http.HttpRequest): HTTP 请求
            approve_request (arkid.core.models.ApproveRequest): 需要同意的审批请求
        """
        pass

    @operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
    def deny_approve_request_handler(self, request, request_id):
        approve_request = ApproveRequest.valid_objects.get(id=request_id)
        self.deny_approve_request(request, approve_request)
        approve_request.status = 'deny'
        approve_request.save()
        return ErrorDict(ErrorCode.OK)

    @abstractmethod
    def deny_approve_request(self, request, approve_request):
        """
        抽象方法
        Args:
            request (django.http.HttpRequest): HTTP 请求
            approve_request (arkid.core.models.ApproveRequest): 需要拒绝的审批请求
        """
        pass

    def create_tenant_config(self, tenant, config, name, type):
        tenant_config = super().create_tenant_config(tenant, config, name, type)
        tenant_config.config["pass_request_url"] = self.pass_path
        tenant_config.config["deny_request_url"] = self.deny_path
        tenant_config.save()
        return tenant_config

    def register_approve_system_schema(self, schema, system_type):
        self.register_config_schema(schema, self.package + '_' + system_type)
        self.register_composite_config_schema(
            schema, system_type, exclude=['extension']
        )
