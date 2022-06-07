#!/usr/bin/env python3
from os import environ
import re
import io
import json
from django.urls import resolve
from arkid.core.models import Tenant
from django.http import HttpResponse
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
        if not approve_action or not approve_action.extension:
            return None

        user = verify_token(request)
        if not user:
            return None

        approve_request = ApproveRequest.valid_objects.filter(
            action=approve_action, user=user
        ).first()
        if not approve_request:
            approve_request = create_approve_request(request, user, approve_action)
            dispatch_event(
                Event(
                    tag=CREATE_APPROVE_REQUEST,
                    tenant=request.tenant,
                    data=approve_request,
                )
            )
            response = HttpResponse(status=401)
            return response
        else:
            if approve_request.status != "pass":
                response = HttpResponse(status=401)
                return response
            else:
                return None
