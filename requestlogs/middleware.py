import json
from .base import SETTINGS
from .logging import set_request_id, validate_uuid
from . import get_requestlog_entry


class RequestLogsMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # DRF sets the `cls` attribute
        if getattr(view_func, 'cls', None):
            get_requestlog_entry(request=request, view_func=view_func)

    def __call__(self, request):
        request.cached_request_body = request.body
        try:
            request.cached_request_data = json.loads(request.cached_request_body)
        except:
            request.cached_request_data = {}

        response = self.get_response(request)

        # handle only methods defined in the settings
        if request.method.upper() in tuple(m.upper() for m in SETTINGS['METHODS']):
            get_requestlog_entry(request).finalize(response)

        return response


class RequestIdMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        reuse_request_id = request.META.get(SETTINGS['REQUEST_ID_HTTP_HEADER'])
        set_request_id(validate_uuid(reuse_request_id))
        return self.get_response(request)
