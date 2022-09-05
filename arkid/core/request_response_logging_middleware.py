import re
import json
import time
from django.urls import resolve
from arkid.core.models import Tenant, User
from arkid.config import get_app_config
from arkid.core.event import (
    Event,
    dispatch_event,
    REQUEST_RESPONSE_LOGGGING,
)


class LoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

        # Filter to log all request to url's that start with any of the strings below.
        self.prefixs = [
        ]

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        start = time.time() # Calculated execution time.
        
        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        exec_time = int((time.time() - start)*1000)

        # If the url does not start with on of the prefixes above, then return response and dont save log.
        # (Remove these two lines below to log everything)
        # if not list(filter(request.get_full_path().startswith, self.prefixs)): 
            # return response

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

        dispatch_event(Event(tag=REQUEST_RESPONSE_LOGGGING, tenant=request.tenant, request=request, response=response, data=request_log))
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            _ip = x_forwarded_for.split(',')[0]
        else:
            _ip = request.META.get('REMOTE_ADDR')
        return _ip