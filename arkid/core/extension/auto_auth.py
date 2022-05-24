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
    composite_key = 'auth_type'
    composite_model = TenantExtension

    @property
    def type(self):
        return AutoAuthExtension.TYPE

    def load(self):
        self.listen_event(core_event.AUTO_LOGIN, self.authenticate)
        self.listen_event(
            core_event.CREATE_AUTO_AUTH_CONFIG, self.create_auto_auth_config
        )
        self.listen_event(
            core_event.UPDATE_AUTO_AUTH_CONFIG, self.update_auto_auth_config
        )
        self.listen_event(
            core_event.DELETE_AUTO_AUTH_CONFIG, self.delete_auto_auth_config
        )
        super().load()

    def authenticate(self, event, **kwargs):
        pass

    def create_auto_auth_config(self, event, **kwargs):
        pass

    def update_auto_auth_config(self, event, **kwargs):
        pass

    def delete_auto_auth_config(self, event, **kwargs):
        pass

    def register_auto_auth_schema(self, schema, auto_auth_type):
        self.register_config_schema(schema, self.package + '_' + auto_auth_type)
        self.register_composite_config_schema(
            schema, auto_auth_type, exclude=['extension']
        )
