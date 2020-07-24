"""
only for saml2.0 dev
"""

from django.views import View
from django.shortcuts import render


class LoginView(View):
    """
    模拟OneID的登录页面
    run as FE
    """
    def get(self, request):    # pylint: disable=no-self-use
        """
        arkid login
        """
        token_url = '/siteapi/v1/ucenter/login/'
        return render(request, 'dev/mock_login.html', context={'token_url': token_url})


class AliyunRoleSSOLoginView(View):
    """
    模拟OneID的登录页面
    run as FE
    """
    def get(self, request):    # pylint: disable=no-self-use
        """
        aliyun role sso login
        """
        token_url = '/siteapi/v1/ucenter/login/'
        return render(request, 'dev/aliyun_role_sso_login.html', context={'token_url': token_url})
