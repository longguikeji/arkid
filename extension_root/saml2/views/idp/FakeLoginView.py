"""
SAML2.0 模拟登陆以获取登陆状态 如果前段没有登陆状态则跳转登陆页
"""

from django.views import View
from django.shortcuts import redirect, render
from config import get_app_config

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
            return redirect(f"{get_app_config().get_host()}{next}&spauthn={token}")

        login_url = f"{get_app_config().get_frontend_host()}/login?tenant={str(tenant_uuid).replace('-','')}&next={next}"
        return render(request, 'saml2/fake_login.html', context={'login_url': login_url, "next": next})
