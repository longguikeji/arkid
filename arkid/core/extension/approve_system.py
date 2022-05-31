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
from arkid.common.logger import logger


class ApproveSystemExtension(Extension):

    TYPE = "approve_system"

    composite_schema_map = {}
    created_composite_schema_list = []
    composite_key = 'type'
    composite_model = TenantExtension

    @property
    def type(self):
        return ApproveSystemExtension.TYPE

    def load(self):
        self.listen_event(
            core_event.CREATE_APPROVE_SYSTEM_CONFIG, self.create_approve_system_config
        )
        self.listen_event(
            core_event.UPDATE_APPROVE_SYSTEM_CONFIG, self.update_approve_system_config
        )
        self.listen_event(
            core_event.DELETE_APPROVE_SYSTEM_CONFIG, self.delete_approve_system_config
        )
        super().load()

    def create_approve_system_config(self, event, **kwargs):
        pass

    def update_approve_system_config(self, event, **kwargs):
        pass

    def delete_approve_system_config(self, event, **kwargs):
        pass

    def register_approve_system_schema(self, schema, system_type):
        self.register_config_schema(schema, self.package + '_' + system_type)
        self.register_composite_config_schema(
            schema, system_type, exclude=['extension']
        )

    @classmethod
    def restore_request(cls, approve_request):
        environ = approve_request.environ
        body = approve_request.body
        environ["wsgi.input"] = io.BytesIO(body)
        request = WSGIRequest(environ)
        request.tenant = approve_request.action.tenant
        request.user = approve_request.user
        view_func, args, kwargs = resolve(request.path)
        klass = view_func.__self__
        operation, _ = klass._find_operation(request)
        response = operation.run(request, **kwargs)
        logger.info(
            f'Restore Request: {approve_request.user.username}:{approve_request.action.method}:{approve_request.action.path}'
        )
        return response
