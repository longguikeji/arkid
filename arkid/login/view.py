from typing import Any
from django.shortcuts import render
from django.views import View
from django.urls import reverse
from django.shortcuts import redirect
from arkid.core.translation import gettext_default as _
from arkid.common.logger import logger
from arkid.core.models import Tenant, ExpiringToken
from arkid.core.event import register_and_dispatch_event, dispatch_event, Event
from ninja import Schema
from arkid.core.token import refresh_token


class AutoLoginSchema(Schema):
    tenant: Any


class LoginEnter(View):
    """ """

    def get(
        self, request, *args, **kwargs
    ):  # pylint: disable=no-self-use unused-argument
        """
        调用sso url 前中转
        """
        params_list = []
        for key in request.GET.keys():
            params_list.append(f"{key}={request.GET[key]}")

        params_str = '&'.join(params_list)

        login_process_url = reverse('login_process')
        return render(
            request,
            'login_enter.html',
            context={"params": params_str, "login_process_url": login_process_url},
        )


class LoginProcess(View):
    """ """

    def get(
        self, request, *args, **kwargs
    ):  # pylint: disable=no-self-use unused-argument
        login_uri = '/login'
        params_list = []
        tenant_id = request.GET.get("tenant")
        if not tenant_id:
            tenant = Tenant.objects.filter(name="platform tenant").first()
        else:
            tenant = Tenant.active_objects.get(id=tenant_id)

        # next = request.GET.get("next")
        token = request.GET.get("token")
        for key in request.GET.keys():
            if key != 'token':
                params_list.append(f"{key}={request.GET[key]}")

        # params_str = '&'.join(params_list)
        if token:
            try:
                token = ExpiringToken.objects.get(token=token)

                if not token.user.is_active:
                    raise Exception(_('User inactive or deleted'))

                if token.expired(tenant):
                    raise Exception(_('Token has expired'))

                params_list.append(f"token={token}")
                params_str = '&'.join(params_list)
                response = redirect(f'{login_uri}?{params_str}')
                return response

            except ExpiringToken.DoesNotExist:
                logger.error(_("Invalid token"))
            except Exception as err:
                logger.error(err)

        # 开启自动化登录
        responses = dispatch_event(
            Event(tag='AUTO_LOGIN', tenant=tenant, request=request)
        )
        if responses:
            for func, (result, ext) in responses:
                if type(result) is not tuple:  # keberos 登录返回user, http_response
                    continue
                user = result[0]
                http_response = result[1]
                if http_response:
                    return http_response
                elif user:
                    token = refresh_token(user)
                    params_list.append(f"token={token}")
                    params_str = '&'.join(params_list)
                    return redirect(f'{login_uri}?{params_str}')
                else:
                    continue

        params_str = '&'.join(params_list)
        return redirect(f'{login_uri}?{params_str}')
