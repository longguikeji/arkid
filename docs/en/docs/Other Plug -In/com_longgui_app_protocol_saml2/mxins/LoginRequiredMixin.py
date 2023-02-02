"""
用户登陆态验证
"""
from django.http import HttpRequest
from arkid.config import get_app_config
import logging
from .AccessMixin import AccessMixin
logger = logging.Logger(__name__)
from arkid.core.models import ExpiringToken as Token
from saml2 import BINDING_HTTP_POST, BINDING_HTTP_REDIRECT
from django.utils.datastructures import MultiValueDictKeyError
from django.core.exceptions import ValidationError

class LoginRequiredMixin(AccessMixin):
    """Verify that the current user is authenticated."""

    def dispatch(self, request, tenant_id, config_id, *args, **kwargs):
        '''检查用户cookies是否登录
        '''
        try:
            token = request.GET.get("token",None)
            token = Token.objects.get(token=token)  # pylint: disable=no-member
            if token:
                request.user = token.user
                return super().dispatch(request, tenant_id, config_id, *args, **kwargs)
        except Token.DoesNotExist as err:    # pylint: disable=broad-except
            return self.handle_no_permission(request.path)
