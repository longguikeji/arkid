#!/usr/bin/env python3

from abc import abstractmethod
from arkid.core.extension import Extension
from arkid.core.translation import gettext_default as _
from arkid.core import event as core_event
from arkid.extension.models import TenantExtensionConfig
from pydantic import Field
from ninja import Schema


class ApproveSystemBaseSchema(Schema):
    change_status_url: str = Field(
        title=_('Change Approve Request Status Url', '改变审批请求URL'), readonly=True
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
        self.path = self.register_api(
            f'/change_approve_request_status/{{approve_request_id}}/',
            'POST',
            self.change_approve_request_status, auth=None
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

    @abstractmethod
    def change_approve_request_status(self, request, approve_request_id):
        """
        抽象方法
        Args:
            request (django.http.HttpRequest): 创建审批请求事件
            approve_request_id (str): 需要改变审批状态的审批请求ID
        """
        pass

    def create_tenant_config(self, tenant, config, name, type):
        tenant_config = super().create_tenant_config(tenant, config, name, type)
        tenant_config.config["change_status_url"] = self.path
        tenant_config.save()
        return tenant_config

    def register_approve_system_schema(self, schema, system_type):
        self.register_config_schema(schema, self.package + '_' + system_type)
        self.register_composite_config_schema(
            schema, system_type, exclude=['extension']
        )
