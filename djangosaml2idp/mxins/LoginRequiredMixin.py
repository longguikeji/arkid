"""
用户登陆态验证
"""
from config import get_app_config
import logging
from rest_framework.authtoken.models import Token
from .AccessMixin import AccessMixin
logger = logging.Logger(__name__)


class LoginRequiredMixin(AccessMixin):
    """Verify that the current user is authenticated."""

    def dispatch(self, request, tenant_uuid, app_id, *args, **kwargs):
        '''检查用户cookies是否登录
        '''
        try:
            spauthn = request.GET.get("spauthn", None) or request.COOKIES["spauthn"]
            token = Token.objects.get(key=spauthn)  # pylint: disable=no-member
            if token:
                request.user = token.user
                return super().dispatch(request, tenant_uuid, app_id, *args, **kwargs)
        except Exception as err:    # pylint: disable=broad-except
            logger.debug(err)
            next = f"{get_app_config().get_host()}{request.path}?{'&'.join([f'{k}={request.GET[k]}'for k in request.GET.keys()])}"
            return self.handle_no_permission(next, tenant_uuid, app_id)
