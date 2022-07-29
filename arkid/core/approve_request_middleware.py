#!/usr/bin/env python3
from os import environ
import re
import io
import json
from django.urls import resolve
from arkid.core.models import Tenant
from django.http import HttpResponse, JsonResponse
from arkid.core.models import ApproveAction, ApproveRequest
from arkid.core.approve import create_approve_request
from arkid.common.utils import verify_token
from pydantic import Field
from arkid.core.event import (
    Event,
    register_event,
    dispatch_event,
    CREATE_APPROVE_REQUEST,
)
from arkid.core.translation import gettext_default as _
from arkid.core.error import ErrorCode, ErrorDict


class ApproveRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        tenant = request.tenant
        path = ('/' + request.resolver_match.route).replace("<", "{").replace(">", "}")
        method = request.method

        approve_action = ApproveAction.valid_objects.filter(
            tenant=tenant, path=path, method=method
        ).first()
        if not approve_action:
            approve_action = ApproveAction.valid_objects.filter(
                tenant=None,
                path=path,
                method=method,
            ).first()

        if not approve_action or not approve_action.extension:
            return None

        user = verify_token(request)
        if not user:
            return None

        # approve_request = ApproveRequest.valid_objects.filter(
        #     action=approve_action, user=user
        # ).first()
        approve_request = self.get_prev_approve_request(request, user, approve_action)
        if not approve_request:
            approve_request = create_approve_request(request, user, approve_action)
            dispatch_event(
                Event(
                    tag=CREATE_APPROVE_REQUEST,
                    tenant=request.tenant,
                    data=approve_request,
                )
            )
            response = JsonResponse(
                ErrorDict(ErrorCode.APPROVE_REQUEST_WAITING),
                status=403,
            )
            return response
        else:
            if approve_request.status != "pass":
                response = JsonResponse(
                    ErrorDict(ErrorCode.APPROVE_REQUEST_WAITING),
                    status=403,
                )
                return response
            else:
                return None

    def get_prev_approve_request(self, request, user, approve_action):
        if request.method == 'GET':
            get_data = request.GET.dict()
            if 'page' in get_data:
                get_data.pop('page')
            if 'page_size' in get_data:
                get_data.pop('page_size')
            approve_request = ApproveRequest.valid_objects.filter(
                action=approve_action,
                user=user,
                request_get=get_data,
                request_path=request.path,
            ).first()
            return approve_request
        elif request.method in ['POST', 'PUT']:
            body_unicode = request.body.decode('utf-8')
            try:
                new_body = json.loads(body_unicode)
            except Exception as e:
                new_body = body_unicode
            approve_request = ApproveRequest.valid_objects.filter(
                action=approve_action,
                user=user,
                request_path=request.path,
            ).first()
            if approve_request:
                stored_body = approve_request.body.decode('utf-8')
                try:
                    old_body = json.loads(stored_body)
                except Exception as e:
                    old_body = stored_body
                if new_body == old_body:
                    return approve_request
        elif request.method == 'DELETE':
            approve_request = ApproveRequest.valid_objects.filter(
                action=approve_action,
                user=user,
                request_path=request.path,
            ).first()
            return approve_request

        return None
