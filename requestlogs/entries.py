import datetime
import time
import json

from django.utils import timezone
from rest_framework.request import Request

from .base import SETTINGS
from .logging import get_request_id
from .utils import remove_secrets, get_client_ip


class RequestHandler(object):
    def __init__(self, request):
        self.request = request

    @property
    def method(self):
        return self.request.method

    @property
    def data(self):
        return remove_secrets(self.request.cached_request_data)

    @property
    def query_params(self):
        return remove_secrets(self.request.GET)

    @property
    def full_path(self):
        return self.request.get_full_path()

    @property
    def path(self):
        return self.request.path

    @property
    def request_id(self):
        return get_request_id()


class DRFRequestHandler(RequestHandler):
    @property
    def data(self):
        return remove_secrets(self.request.data)

    @property
    def query_params(self):
        return self.request.query_params


class ResponseHandler(object):
    def __init__(self, response):
        self.response = response

    @property
    def status_code(self):
        return self.response.status_code

    @property
    def data(self):
        data = getattr(self.response, 'data', None)
        if isinstance(data, dict):
            return remove_secrets(data)
        
        try:
            data = json.loads(self.response.content)
        except:
            pass

        return data


class RequestLogEntry(object):
    """The default requestlog entry class"""

    django_request_handler = RequestHandler
    drf_request_handler = DRFRequestHandler
    response_handler = ResponseHandler

    # Private attributes to hold some context
    _user = None
    _drf_request = None

    def __init__(self, request, view_func):
        self.django_request = request
        self.view_func = view_func
        self.view_class = getattr(view_func, 'cls', None)
        # TODO: How to get view_obj at this point?
        self.view_obj = None
        self._initialized_at = time.time()

    def finalize(self, response):
        renderer_context = getattr(response, 'renderer_context', {})

        self.view_obj = renderer_context.get('view')

        if not self.drf_request:
            self.drf_request = renderer_context.get('request')

        if self.drf_request:
            self.request = self.drf_request_handler(self.drf_request)
        else:
            self.request = self.django_request_handler(self.django_request)

        self.response = self.response_handler(response)
        self.store()

    def store(self):
        storage = SETTINGS['STORAGE_CLASS']()
        storage.store(self)

    @property
    def user(self):
        ret = {
            'id': None,
            'username': None,
        }

        user = self._user or getattr(self.django_request, 'user', None)
        if user and user.is_authenticated:
            ret['id'] = user.pk
            ret['username'] = user.username

        return ret

    @user.setter
    def user(self, user):
        self._user = user

    @property
    def drf_request(self):
        return self._drf_request

    @drf_request.setter
    def drf_request(self, drf_request):
        assert isinstance(drf_request, (Request, type(None)))
        self._drf_request = drf_request

    @property
    def action_name(self):
        if not self.view_class:
            return None
        action_names = getattr(self.view_class, 'requestlogs_action_names', {})
        try:
            return action_names[self.view_obj.action]
        except (KeyError, AttributeError):
            try:
                return action_names[self.django_request.method.lower()]
            except KeyError:
                pass

    @property
    def ip_address(self):
        return get_client_ip(self.django_request)

    @property
    def timestamp(self):
        return timezone.now()

    @property
    def execution_time(self):
        return datetime.timedelta(seconds=time.time() - self._initialized_at)
