"""
SAML2.0协议 IDP发起登陆前钩子视图 用于获取当前登陆状态
"""

from django.shortcuts import render
from django.views import View
from app.models import App


class SsoHook(View):
    """
    登陆前钩子视图 用于获取当前登陆状态
    """
    def get(self, request, tenant_uuid, app_id):    # pylint: disable=no-self-use unused-argument
        """
        调用sso url 前中转
        """
        spauthn = request.GET.get("spauthn",None)
        app = App.active_objects.get(id=app_id)
        return render(request, 'djangosaml2idp/hook.html', context={'sso_url': app.data["sso_url"], "spauthn": spauthn})
