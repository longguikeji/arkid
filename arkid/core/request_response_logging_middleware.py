import re
import json
import time
import traceback
from django.urls import resolve
from arkid.core.models import Tenant, User
from arkid.config import get_app_config
from arkid.core.event import (
    Event,
    dispatch_event,
    REQUEST_RESPONSE_LOGGGING,
)
from arkid.common.logger import logger


class LoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

        # Filter to log all request to url's that does not start with any of the strings below.
        self.prefixs = [
            "/api/v1/ping/"
        ]

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        start = time.time() # Calculated execution time.
        
        try:
            response = self.get_response(request)
        except Exception as e:
            exec_time = int((time.time() - start)*1000)
            self.send_error_log_to_arkid_saas(request, exec_time, traceback.format_exc())
            raise e
        else:
            # Code to be executed for each request/response after
            # the view is called.

            exec_time = int((time.time() - start)*1000)

            # If the url starts with on of the prefixes above, then return response and dont save log.
            # (Remove these two lines below to log everything)
            if list(filter(request.get_full_path().startswith, self.prefixs)): 
                return response

            try:
                body_request = str(request.body.decode())
            except:
                body_request = ""

            try:
                body_response = str(response.content.decode())
            except:
                body_response = ""

            # Create instance and assign values
            request_log = dict(
                endpoint=request.get_full_path(),
                response_code=response.status_code,
                method=request.method,
                remote_address=self.get_client_ip(request),
                exec_time=exec_time,
                body_request=body_request,
                body_response=body_response,
            )

            # Assign user to log if it's not an anonymous user
            # if not request.user.is_anonymous:
            #     request_log.user = request.user
            dispatch_event(Event(tag=REQUEST_RESPONSE_LOGGGING, tenant=Tenant.platform_tenant(), request=request, response=response, data=request_log))

        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            _ip = x_forwarded_for.split(',')[0]
        else:
            _ip = request.META.get('REMOTE_ADDR')
        return _ip

    def send_error_log_to_arkid_saas(self, request, exec_time, traceback_info):
        try:
            user = request.user
            tenant = request.tenant
            # AnonymousUser
            if not isinstance(user, User):
                user = None
            # print("request and response logging data: ", data)
            try:
                is_tenant_admin = tenant.has_admin_perm(user)
            except Exception as e:
                is_tenant_admin = False

            # request_path = request.path
            status_code = 500
            if user:
                username = user.username
            else:
                try:
                    response_body = json.loads(data["body_response"])
                    username = response_body["data"]["user"]["username"]
                except:
                    username = None

            try:
                body_request = str(request.body.decode())
            except:
                body_request = ""

            body_response = traceback_info

            data = dict(
                endpoint=request.get_full_path(),
                response_code=status_code,
                method=request.method,
                remote_address=self.get_client_ip(request),
                exec_time=exec_time,
                body_request=body_request,
                body_response=body_response,
            )

            tenant_id = tenant.id.hex
            user_id = user and user.id.hex
            request_path = request.build_absolute_uri()

            from arkid.core.tasks.celery import dispatch_task
            dispatch_task.delay('upload_error_log_to_arkid_saas', tenant_id, user_id, is_tenant_admin, data, username, \
                request_path, status_code)
        except Exception as e:
            logger.error(f"send_error_log_to_arkid_saas failed: {e}")