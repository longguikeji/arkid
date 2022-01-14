"""
用户登陆态验证
"""

from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext_lazy as _
import logging
from app.models import App

logger = logging.Logger(__name__)


class AppLoginRequiredMixin:
    """Verify that the current user is authenticated."""

    def dispatch(self, request, tenant_uuid, app_id, *args, **kwargs):
        '''检查用户cookies是否登录
        '''
        # try:
        print(request.POST)

        client_id = request.POST.get("client_id")
        client_secret = request.POST.get("client_secret")

        app = App.active_objects.filter(
            uuid=app_id,
        ).first()

        if app:
            request.app = app
            return super().dispatch(request, tenant_uuid, app_id, *args, **kwargs)
        else:
            raise PermissionDenied(_("应用信息有误：请检查client_id等信息是否正确"))
        # except Exception as err:    # pylint: disable=broad-except
        #     raise PermissionDenied(_("鉴权错误：请联系管理员"))
