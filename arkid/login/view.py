from typing import Any
from django.shortcuts import render
from django.views import View
from django.urls import reverse
from django.shortcuts import redirect
from arkid.core.translation import gettext_default as _
from arkid.common.logger import logger
from arkid.core.models import Tenant, ExpiringToken
from arkid.core.event import register_and_dispatch_event
from ninja import Schema


class AutoLoginSchema(Schema):
    tenant: Any


class LoginEnter(View):
    """
    """
    def get(self, request, *args, **kwargs):    # pylint: disable=no-self-use unused-argument
        """
        调用sso url 前中转
        """
        params_list = []
        for key in request.GET.keys():
            params_list.append(f"{key}={request.GET[key]}")
        
        params_str = '&'.join(params_list)
        
        login_process_url = reverse('api:login_process')
        return render(request, 'login_enter.html', context={"params": params_str,"login_process_url":login_process_url})


class LoginProcess(View):
    """
    """
    def get(self, request, *args, **kwargs):    # pylint: disable=no-self-use unused-argument
        params_list = []
        tenant__uuid = request.GET.get("tenant")
        tenant = Tenant.active_objects.get(uuid=tenant__uuid)
        
        next = request.GET.get("next")
        for key in request.GET.keys():
            if key != 'next' and key != 'token':
                params_list.append(f"{key}={request.GET[key]}")
        
        params_str = '&'.join(params_list)
        token = request.GET.get("token")
        try:
            token = ExpiringToken.objects.get(token=token)
            
            if not token.user.is_active:
                raise Exception(_('User inactive or deleted'))

            if token.expired():
                raise Exception(_('Token has expired'))
            
            response = redirect(
                next+f"&{params_str}&token={token}&is_hooked=True"
            )
            
            return response
                
        except ExpiringToken.DoesNotExist:
            logger.error(_("Invalid token"))
        except Exception as err:
            logger.error(err)
        
        # 开启自动化登录
        response = register_and_dispatch_event(tag='AUTO_LOGIN', name=_('自动登录'), tenant=tenant)
        if response:
            for _, user in response:
                if user:
                    token = ExpiringToken(user=user)
                    token.save()
                    return redirect(f'{login_uri}?next={next}&{params_str}&token={token.token}&is_hooked=True')

        # provider = runtime.login_page_provider()
        # login_uri = provider.login_page_url(tenant) or '/login'
        # 租户自定义登录页面
        login_uri = '/login'
        
        return redirect(f'{login_uri}?next={next}&{params_str}&is_hooked=True')
