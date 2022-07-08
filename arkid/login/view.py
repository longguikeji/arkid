from typing import Any
from django.shortcuts import render
from django.views import View
from django.urls import reverse
from django.shortcuts import redirect
from arkid.core.translation import gettext_default as _
from arkid.common.logger import logger
from arkid.core.models import Tenant, ExpiringToken
from arkid.core.event import dispatch_event, AUTO_LOGIN, Event
from ninja import Schema
from arkid.core.models import User
from arkid.core.token import refresh_token

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
        
        login_process_url = reverse('login_process')
        return render(request, 'login_enter.html', context={"params": params_str,"login_process_url":login_process_url})


class LoginProcess(View):
    """
    """
    def get(self, request, *args, **kwargs):    # pylint: disable=no-self-use unused-argument
        params_list = []

        # provider = runtime.login_page_provider()
        # login_uri = provider.login_page_url(tenant) or '/login'
        # 租户自定义登录页面
        login_uri = '/login'

        tenant = request.tenant

        next = request.GET.get("next", "")
        for key in request.GET.keys():
            if key != 'next' and key != 'token':
                params_list.append(f"{key}={request.GET[key]}")
        
        params_str = '&'.join(params_list)
        token = request.GET.get("token")
        try:
            token = ExpiringToken.objects.get(token=token)
            
            if not token.user.is_active:
                raise Exception(_('User inactive or deleted'))

            if token.expired(tenant):
                raise Exception(_('Token has expired'))
            
            if next:
                if '?' in next:
                    response = redirect(
                        next+f"&token={token}&{params_str}"
                    )
                else:
                    response = redirect(
                        next+f"?token={token}&{params_str}"
                    )
            else:
                response = redirect(f'{login_uri}?token={token}&{params_str}')
            
            return response
                
        except ExpiringToken.DoesNotExist:
            logger.error(_("Invalid token"))
        except Exception as err:
            logger.error(err)
        
        # 开启自动化登录
        response = dispatch_event(Event(AUTO_LOGIN, tenant=tenant, request=request))
        if response:
            for func, (result, ext) in response:
                if type(result) is User:
                    token = refresh_token(result)
                    return redirect(f'/api/v1/login/?next={next}&token={token}&{params_str}')
                elif result is None:
                    continue
                else:
                    return result

       
        if params_str:
            return redirect(f'{login_uri}?next={next}&{params_str}')
        else:
            return redirect(f'{login_uri}?next={next}')