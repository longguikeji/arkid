"""
SAML2.0 模拟登陆以获取登陆状态 如果前段没有登陆状态则跳转登陆页
"""

from django.urls.base import reverse
from django.views import View
from django.shortcuts import render


class FakeLogin(View):
    """
    模拟登录页面 无操作 获取前端登陆状态  如无则直接跳转登陆页面
    """

    def get(self, request, tenant_uuid, app_id):    # pylint: disable=no-self-use
        """
        arkid login
        """
        token_url = reverse("api:login")
        return render(request, 'djangosaml2idp/fake_login.html', context={'token_url': token_url, "next": reverse("api:saml2idp:saml_login_process", args=(tenant_uuid, app_id))})
