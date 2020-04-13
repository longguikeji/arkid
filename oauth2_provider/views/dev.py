'''
only for dev

用于示意不同域名下的token存取
OneID API: 127.0.0.1:8080
OneID FE: localhost:7070
'''

from django.views import View
from django.shortcuts import render


class LoginView(View):
    '''
    模拟OneID的登录页面
    run as FE
    '''
    def get(self, request):
        token_url = '/siteapi/v1/ucenter/login/'
        return render(request, 'oauth2_provider/dev/mock_login.html', context={'token_url': token_url})


class TokenView(View):
    '''
    在OAuth2开始时（访问/authorize），先到OneID FE获取Token用于检查登录状态
    run as FE
    '''
    def get(self, request):
        return render(request, 'oauth2_provider/dev/token.html')
