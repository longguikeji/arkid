#!/usr/bin/env python3
from os import environ
import re
import io
import json
from django.urls import resolve
from arkid.core.models import Tenant
from django.http import HttpResponse
from arkid.core.models import ApproveAction, ApproveRequest
from arkid.core.models import ExpiringToken
from django.core.handlers.wsgi import WSGIRequest


class ApproveRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        tenant = request.tenant
        path = request.path
        method = request.method

        user = self.get_user(request)
        approve_action = ApproveAction.valid_objects.filter(
            tenant=tenant, path=path, method=method
        ).first()
        if not user or not approve_action:
            response = self.get_response(request)
            return response

        approve_request = ApproveRequest.valid_objects.filter(
            action=approve_action, user=user
        ).first()
        if not approve_request:
            environ = request.environ
            environ.pop("wsgi.input")
            environ.pop("wsgi.errors")
            environ.pop("wsgi.file_wrapper")
            approve_request = ApproveRequest.valid_objects.create(
                action=approve_action,
                user=user,
                environ=environ,
                body=request.body,
            )
            response = HttpResponse(status=401)
            return response
        else:
            if approve_request.status != "pass":
                response = HttpResponse(status=401)
                return response
            else:
                response = self.get_response(request)
                return response
                # 测试如果通过后，重新执行ninja function view
                # self.restore_request(approve_request)

        # Code to be executed for each request/response after
        # the view is called.
        #

    def process_view(self, request, view_func, view_args, view_kwargs):
        return None

    def get_user(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None
        token = auth_header.split(" ")[1]
        try:
            token = ExpiringToken.objects.get(token=token)

            if not token.user.is_active:
                return None

            if token.expired(request.tenant):
                return None

        except ExpiringToken.DoesNotExist:
            return None
        except Exception as err:
            return None

        return token.user

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
