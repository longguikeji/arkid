"""
SAML2.0 模拟登陆以获取登陆状态 如果前段没有登陆状态则跳转登陆页
"""

from django.urls.base import reverse
from django.views import View
from django.shortcuts import redirect, render
from config import get_app_config
import urllib

class FakeLogin(View):
    
    """
    模拟登录页面 无操作 获取前端登陆状态  如无则直接跳转登陆页面
    """

    def get(self, request, tenant_uuid, app_id):    # pylint: disable=no-self-use
        """
        arkid login
        """
        next = request.GET.get("next",None)
        if request.GET.get("token",None):
            token = request.GET.get("token")
            params=[f'{k}={request.GET[k]}' for k in request.GET.keys() if k != "token" ]
            return redirect(f"{next}&spauthn={token}")

        params=[f'{k}={request.GET[k]}' for k in request.GET.keys() ]
        login_url = f"{get_app_config().get_frontend_host()}/login?tenant={str(tenant_uuid).replace('-','')}&next={next}"
        # login_url = urllib.parse.quote(login_url)
        return render(request, 'djangosaml2idp/fake_login.html', context={'login_url': login_url, "next": next})
