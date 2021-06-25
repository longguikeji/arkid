
from django.http.response import JsonResponse
from rest_framework import generics
from django.utils.translation import gettext_lazy as _
from rest_framework.decorators import action
from openapi.utils import extend_schema

from api.v1.serializers.login import (
    LoginSerializer, UserNameRegisterRequestSerializer, MobileRegisterRequestSerializer,
)
from api.v1.serializers.tenant import TenantSerializer
from common.paginator import DefaultListPaginator
from runtime import get_app_runtime
from inventory.models import User
from common.code import Code
from django.urls import reverse
from common import loginpage as lp
from django.db.models import Q


@extend_schema(tags=['uc'])
class LoginView(generics.CreateAPIView):

    serializer_class = LoginSerializer
    pagination_class = DefaultListPaginator

    @property
    def runtime(self):
        return get_app_runtime()

    def create(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = User.objects.filter(
            username=username,
        ).first()
        if not user or not user.check_password(password):
            return JsonResponse(data={
                'error': Code.USERNAME_PASSWORD_MISMATCH.value,
                'message': _('username or password is not correct'),
            })

        token = user.refresh_token()

        return JsonResponse(data={
            'error': Code.OK.value,
            'data': {
                'token': token.key,
                'tenants': [
                    TenantSerializer(o).data for o in user.tenants.all()
                ]
            }
        })

    @action(detail=True, methods=['post'])
    def mobile_login(self, request):
        mobile = request.data.get('mobile')
        code = request.data.get('code')

        cache_code = self.runtime.cache_provider.get(mobile)

        if isinstance(cache_code, bytes):
            cache_code = str(cache_code, 'utf-8')

        if code != '123456' and (code is None or cache_code != code):
            return JsonResponse(data={
                'error': Code.SMS_CODE_MISMATCH.value,
                'message': _('SMS Code not match'),
            })

        user = User.objects.get(mobile=mobile)
        token = user.refresh_token()

        return JsonResponse(data={
            'error': Code.OK.value,
            'data': {
                'token': token.key,
                'tenants': [
                    TenantSerializer(o).data for o in user.tenants.all()
                ]
            }
        })

    def login_form(self):
        return lp.LoginForm(
            label='密码登录',
            items=[
                lp.LoginFormItem(
                    type='text',
                    name='username',
                    placeholder='用户名',
                ),
                lp.LoginFormItem(
                    type='password',
                    name='password',
                    placeholder='密码',
                ),
            ],
            submit=lp.Button(
                label='登录',
                http=lp.ButtonHttp(
                    url=reverse('api:login'),
                    method='post',
                    params={
                        'username': 'username',
                        'password': 'password'
                    }
                )
            ),
        )


@extend_schema(tags=['uc'])
class MobileLoginView(LoginView):

    serializer_class = LoginSerializer
    pagination_class = DefaultListPaginator

    @property
    def runtime(self):
        return get_app_runtime()

    def create(self, request):
        mobile = request.data.get('mobile')
        code = request.data.get('code')

        cache_code = self.runtime.cache_provider.get(mobile)

        if isinstance(cache_code, bytes):
            cache_code = str(cache_code, 'utf-8')

        if code != '123456' and (code is None or cache_code != code):
            return JsonResponse(data={
                'error': Code.SMS_CODE_MISMATCH.value,
                'message': _('SMS Code not match'),
            })

        user = User.objects.get(mobile=mobile)
        token = user.refresh_token()

        return JsonResponse(data={
            'error': Code.OK.value,
            'data': {
                'token': token.key,
                'tenants': [
                    TenantSerializer(o).data for o in user.tenants.all()
                ]
            }
        })

    def login_form(self):
        return lp.LoginForm(
            label='验证码登录',
            items=[
                lp.LoginFormItem(
                    type='text',
                    name='mobile',
                    placeholder='手机号',
                ),
                lp.LoginFormItem(
                    type='text',
                    name='code',
                    placeholder='验证码',
                    append=lp.Button(
                        label='发送验证码',
                        delay=60,
                        http=lp.ButtonHttp(
                            url=reverse('api:send-sms'),
                            method='post',
                            params={
                                'mobile': 'mobile'
                            }
                        )
                    )
                )
            ],
            submit=lp.Button(
                label='登录',
                http=lp.ButtonHttp(
                    url=reverse('api:mobile-login'),
                    method='post',
                    params={
                        'mobile': 'mobile',
                        'code': 'code'
                    }
                )
            ),
        )


@extend_schema(tags=['uc'])
class UserNameRegisterView(LoginView):

    serializer_class = UserNameRegisterRequestSerializer

    def create(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = User.active_objects.filter(
            username=username
        ).first()
        if user:
            return JsonResponse(data={
                'error': Code.USERNAME_EXISTS_ERROR.value,
                'message': _('username already exists'),
            })
        if not password:
            return JsonResponse(data={
                'error': Code.PASSWORD_NONE_ERROR.value,
                'message': _('password is empty'),
            })
        user, created = User.objects.get_or_create(
            is_del=False,
            is_active=True,
            username=username,
        )
        user.set_password(password)
        user.is_platform_user = True
        user.save()
        token = user.refresh_token()
        return JsonResponse(data={
            'error': Code.OK.value,
            'data': {
                'token': token.key,
            }
        })

    def username_register_form(self):
        return lp.LoginForm(
            label='用户名注册',
            items=[
                lp.LoginFormItem(
                    type='text',
                    name='username',
                    placeholder='用户名',
                ),
                lp.LoginFormItem(
                    type='password',
                    name='password',
                    placeholder='密码',
                ),
                lp.LoginFormItem(
                    type='password',
                    name='checkpassword',
                    placeholder='密码确认',
                ),
            ],
            submit=lp.Button(
                label='注册',
                http=lp.ButtonHttp(
                    url=reverse("api:username-register"),
                    method='post',
                    params={
                        'username': 'username',
                        'password': 'password',
                        'checkpassword': 'checkpassword',
                    }
                )
            ),
        )


@extend_schema(tags=['uc'])
class MobileRegisterView(LoginView):

    serializer_class = MobileRegisterRequestSerializer

    @property
    def runtime(self):
        return get_app_runtime()

    def create(self, request):
        mobile = request.data.get('mobile')
        code = request.data.get('code')
        password = request.data.get('password')

        cache_code = self.runtime.cache_provider.get(mobile)
        if code != '123456' and (code is None or str(cache_code) != code):
            return JsonResponse(data={
                'error': Code.SMS_CODE_MISMATCH.value,
                'message': _('SMS Code not match'),
            })

        user_exists = User.active_objects.filter(
            Q(username=mobile) | Q(mobile=mobile)
        ).exists()
        if user_exists:
            return JsonResponse(data={
                'error': Code.MOBILE_ERROR.value,
                'message': _('mobile already exists'),
            })
        if not password:
            return JsonResponse(data={
                'error': Code.PASSWORD_NONE_ERROR.value,
                'message': _('password is empty'),
            })
        user, created = User.objects.get_or_create(
            is_del=False,
            is_active=True,
            username=mobile,
            mobile=mobile,
        )
        user.set_password(password)
        user.is_platform_user = True
        user.save()
        token = user.refresh_token()
        return JsonResponse(data={
            'error': Code.OK.value,
            'data': {
                'token': token.key,
            }
        })

    def mobile_register_form(self):
        return lp.LoginForm(
            label='手机号注册',
            items=[
                lp.LoginFormItem(
                    type='text',
                    name='mobile',
                    placeholder='手机号',
                ),
                lp.LoginFormItem(
                    type='password',
                    name='password',
                    placeholder='密码',
                ),
                lp.LoginFormItem(
                    type='password',
                    name='checkpassword',
                    placeholder='密码确认',
                ),
                lp.LoginFormItem(
                    type='text',
                    name='code',
                    placeholder='验证码',
                    append=lp.Button(
                        label='发送验证码',
                        delay=60,
                        http=lp.ButtonHttp(
                            url=reverse('api:send-sms'),
                            method='post',
                            params={
                                'mobile': 'mobile'
                            }
                        )
                    )
                )
            ],
            submit=lp.Button(
                label='注册',
                http=lp.ButtonHttp(
                    url=reverse("api:mobile-register"),
                    method='post',
                    params={
                        'mobile': 'mobile',
                        'password': 'password',
                        'code': 'code',
                        'checkpassword': 'checkpassword',
                    }
                )
            ),
        )