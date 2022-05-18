#!/usr/bin/env python3

import io
from abc import abstractmethod
from arkid.core.extension import Extension
from arkid.core.translation import gettext_default as _
from arkid.core.models import App, ApproveRequest
from arkid.core import api as core_api, event as core_event
from arkid.extension.models import TenantExtensionConfig, TenantExtension
from django.urls import re_path
from django.urls import resolve
from django.core.handlers.wsgi import WSGIRequest
from arkid.core.api import api
from ninja import ModelSchema
from typing import List
from ninja.pagination import paginate
from django.shortcuts import get_object_or_404
from arkid.core.error import ErrorCode


class AccountLifeExtension(Extension):

    TYPE = "account_life"

    composite_schema_map = {}
    created_composite_schema_list = []
    composite_key = 'type'
    composite_model = TenantExtensionConfig

    @property
    def type(self):
        return AccountLifeExtension.TYPE

    def load(self):
        self.listen_event(
            core_event.CREATE_ACCOUNT_LIFE_CONFIG, self.create_account_life_config
        )
        self.listen_event(
            core_event.UPDATE_ACCOUNT_LIFE_CONFIG, self.update_account_life_config
        )
        self.listen_event(
            core_event.DELETE_ACCOUNT_LIFE_CONFIG, self.delete_account_life_config
        )
        super().load()

    def create_account_life_config(self, event, **kwargs):
        pass

    def update_account_life_config(self, event, **kwargs):
        pass

    def delete_account_life_config(self, event, **kwargs):
        pass

    def register_account_life_schema(self, schema, config_type):
        self.register_config_schema(schema, self.package + '_' + config_type)
        self.register_composite_config_schema(
            schema, config_type, exclude=['extension']
        )
