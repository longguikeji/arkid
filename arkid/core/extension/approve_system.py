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


class ApproveRequestOut(ModelSchema):
    class Config:
        model = ApproveRequest
        model_fields = ['id', 'status']

    username: str
    path: str
    method: str

    @staticmethod
    def resolve_username(obj):
        return obj.user.username

    @staticmethod
    def resolve_path(obj):
        return obj.action.path

    @staticmethod
    def resolve_method(obj):
        return obj.action.method


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
        @api.get(
            "/tenant/{tenant_id}/approve_system_arkid/approve_requests/",
            response=List[ApproveRequestOut],
            tags=['审批请求'],
            auth=None,
            operation_id=f'{self.name}_list_approve_requests',
        )
        @paginate
        def approve_request_list(request, tenant_id: str):
            requests = ApproveRequest.valid_objects.filter(
                action__extension__type=self.type
            )
            return requests

        @api.put(
            "/tenant/{tenant_id}/approve_system_arkid/approve_requests/{request_id}/",
            # response=ApproveRequestOut,
            tags=['审批请求'],
            auth=None,
            operation_id=f'{self.name}_process_approve_request',
        )
        def approve_request_process(
            request, tenant_id: str, request_id: str, action: str = ''
        ):
            approve_request = get_object_or_404(ApproveRequest, id=request_id)
            if action == "pass":
                approve_request.status = "pass"
                approve_request.save()
                response = self.restore_request(approve_request)
                return response
            elif action == "deny":
                approve_request.status = "deny"
                approve_request.save()
                return {'error': ErrorCode.OK.value}

        super().load()

    def register_approve_system_schema(self, schema, system_type):
        self.register_config_schema(schema, self.package + '_' + system_type)
        self.register_composite_config_schema(
            schema, system_type, exclude=['extension']
        )

    def restore_request(self, approve_request):
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
        print(response)
        return response
