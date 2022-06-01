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
        super().load()

    def register_account_life_schema(self, schema, config_type):
        self.register_config_schema(schema, self.package + '_' + config_type)
        self.register_composite_config_schema(
            schema, config_type, exclude=['extension']
        )
