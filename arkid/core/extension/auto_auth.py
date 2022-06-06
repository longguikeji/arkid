#!/usr/bin/env python3

import io
from abc import abstractmethod
from arkid.core.extension import Extension
from arkid.core.translation import gettext_default as _
from arkid.core import api as core_api, event as core_event
from arkid.extension.models import TenantExtensionConfig, TenantExtension


class AutoAuthExtension(Extension):

    TYPE = "auto_auth"

    composite_schema_map = {}
    created_composite_schema_list = []
    composite_key = 'type'
    composite_model = TenantExtensionConfig

    @property
    def type(self):
        return AutoAuthExtension.TYPE

    def load(self):
        self.listen_event(core_event.AUTO_LOGIN, self.authenticate)

        super().load()

    @abstractmethod
    def authenticate(self, event, **kwargs):
        """
        抽象方法
        Args:
            event (arkid.core.event.Event): 自动认证事件
        Returns:
            Union[arkid.core.models.User, django.http.HttpResponse]: 自动认证返回结果
        """
        pass

    def register_auto_auth_schema(self, schema, auto_auth_type):
        self.register_config_schema(schema, self.package + '_' + auto_auth_type)
        self.register_composite_config_schema(
            schema, auto_auth_type, exclude=['extension']
        )
