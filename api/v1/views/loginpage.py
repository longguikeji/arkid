from rest_framework import views
from ..serializers import loginpage as lp
from common import loginpage as model
from openapi.utils import extend_schema
from django.http.response import JsonResponse
from api.v1.views.login import (
    LoginView,
    MobileLoginView,
    UserNameRegisterView,
    MobileRegisterView,
)
from api.v1.views.tenant import TenantViewSet
from tenant.models import Tenant, TenantConfig, TenantPrivacyNotice
from external_idp.models import ExternalIdp
from api.v1.serializers.tenant import TenantExtendSerializer
from system.models import SystemConfig, SystemPrivacyNotice
from django.urls import reverse


@extend_schema(tags=['login page'])
class LoginPage(views.APIView):
    @extend_schema(responses=lp.LoginPagesSerializer)
    def get(self, request):
        tenant_uuid = request.query_params.get('tenant', None)
        tenant = Tenant.objects.filter(uuid=tenant_uuid).first()

        data = model.LoginPages()
        if tenant:
            data.setTenant(TenantExtendSerializer(instance=tenant).data)

            # 获取 tenant的登录注册配置
            tenant_config = TenantConfig.objects.filter(
                is_del=False,
                tenant=tenant,
            ).first()
            if not tenant_config:
                mobile_login_register_enabled = (True,)
                secret_login_register_enabled = (True,)
                secret_login_register_field_names = ['username', 'email']
            else:
                mobile_login_register_enabled = tenant_config.data.get(
                    'mobile_login_register_enabled', True
                )
                secret_login_register_enabled = tenant_config.data.get(
                    'secret_login_register_enabled', True
                )
                secret_login_register_field_names = tenant_config.data.get(
                    'secret_login_register_field_names', ['username', 'email']
                )

            if mobile_login_register_enabled:
                data.addForm(
                    model.LOGIN, TenantViewSet().mobile_login_form(tenant_uuid)
                )
                data.addForm(
                    model.REGISTER, TenantViewSet().mobile_register_form(tenant_uuid)
                )
            if secret_login_register_enabled:
                data.addForm(
                    model.LOGIN,
                    TenantViewSet().native_field_login_form(
                        request, tenant_uuid, secret_login_register_field_names
                    ),
                )
            for field_name in secret_login_register_field_names:
                data.addForm(
                    model.REGISTER,
                    TenantViewSet().native_field_register_form(tenant_uuid, field_name),
                )

            external_idps = ExternalIdp.valid_objects.filter(tenant=tenant)
            for idp in external_idps:
                if idp.type not in ['miniprogram']:
                    data.addExtendButton(
                        model.LOGIN,
                        model.Button(
                            img=idp.data['img_url'],
                            tooltip=idp.type,
                            redirect=model.ButtonRedirect(
                                url=idp.data['login_url'],
                            ),
                        ),
                    )
            if data.getPage(model.LOGIN) and data.getPage(model.LOGIN).get(
                'extend', None
            ):
                data.setExtendTitle(model.LOGIN, '第三方登录')
        else:
            data.addForm(model.LOGIN, LoginView().login_form())
            data.addForm(model.LOGIN, MobileLoginView().login_form())
            system_config = self.get_system_config()
            is_open_register = system_config.get('is_open_register', True)
            if is_open_register == True:
                data.addForm(
                    model.REGISTER, UserNameRegisterView().username_register_form()
                )
                data.addForm(
                    model.REGISTER, MobileRegisterView().mobile_register_form()
                )

        # 获取system和tenant中关于隐私声明的配置
        if tenant:
            privacy_notice = TenantPrivacyNotice.valid_objects.filter(
                tenant=tenant
            ).first()
        else:
            privacy_notice = SystemPrivacyNotice.valid_objects.filter().first()
        if privacy_notice:
            agreement = {
                'title': privacy_notice.title,
                'content': privacy_notice.content,
            }
        else:
            agreement = {'title': '', 'content': ''}

        if data.getPage(model.REGISTER):
            data.addBottom(
                model.LOGIN,
                model.Button(
                    prepend='还没有账号，',
                    label='立即注册',
                    gopage=model.REGISTER,
                    agreement=agreement,
                ),
            )
            data.addBottom(
                model.REGISTER,
                model.Button(prepend='已有账号，', label='立即登录', gopage=model.LOGIN),
            )

        if data.getPage(model.LOGIN):
            data.addBottom(model.LOGIN, model.Button(label='忘记密码', gopage='password'))
            data.addForm(model.PASSWORD, self.mobile_password_reset_form())
            data.addForm(model.PASSWORD, self.email_password_reset_form())
            data.addBottom(
                model.PASSWORD,
                model.Button(
                    prepend='还没有账号，',
                    label='立即注册',
                    gopage=model.REGISTER,
                    agreement=agreement,
                ),
            )
            data.addBottom(
                model.PASSWORD,
                model.Button(prepend='已有账号，', label='立即登录', gopage=model.LOGIN),
            )

        pages = lp.LoginPagesSerializer(data=data)
        pages.is_valid()
        return JsonResponse(pages.data)

    def get_system_config(self):
        # 获取基础配置信息
        result = {'is_open_register': True}
        systemconfig = SystemConfig.active_objects.first()
        if systemconfig:
            result = systemconfig.data
        return result

    def mobile_password_reset_form(self):
        tenant_uuid = 'xxxx'
        return model.LoginForm(
            label='通过手机号修改密码',
            items=[
                model.LoginFormItem(
                    type='text',
                    name='mobile',
                    placeholder='手机号',
                ),
                model.LoginFormItem(
                    type='password',
                    name='password',
                    placeholder='新密码',
                ),
                model.LoginFormItem(
                    type='password',
                    name='checkpassword',
                    placeholder='新密码确认',
                ),
                model.LoginFormItem(
                    type='text',
                    name='code',
                    placeholder='验证码',
                    append=model.Button(
                        label='发送验证码',
                        delay=60,
                        http=model.ButtonHttp(
                            url=reverse('api:send-sms'),
                            method='post',
                            params={'mobile': 'mobile'},
                        ),
                    ),
                ),
            ],
            submit=model.Button(
                label='确认',
                http=model.ButtonHttp(
                    url=reverse(
                        "api:tenant-mobile-register",
                        args=[
                            tenant_uuid,
                        ],
                    ),
                    method='post',
                    params={
                        'mobile': 'mobile',
                        'password': 'password',
                        'code': 'code',
                        'checkpassword': 'checkpassword',
                    },
                ),
            ),
        )

    def email_password_reset_form(self):
        tenant_uuid = 'xxxx'
        return model.LoginForm(
            label='通过邮箱修改密码',
            items=[
                model.LoginFormItem(
                    type='text',
                    name='email',
                    placeholder='email账号',
                ),
                model.LoginFormItem(
                    type='password',
                    name='password',
                    placeholder='新密码',
                ),
                model.LoginFormItem(
                    type='password',
                    name='checkpassword',
                    placeholder='新密码确认',
                ),
                model.LoginFormItem(
                    type='text',
                    name='code',
                    placeholder='验证码',
                    append=model.Button(
                        label='发送验证码',
                        delay=60,
                        http=model.ButtonHttp(
                            url=reverse('api:send-sms'),
                            method='post',
                            params={'email': 'email'},
                        ),
                    ),
                ),
            ],
            submit=model.Button(
                label='确认',
                http=model.ButtonHttp(
                    url=reverse(
                        "api:tenant-mobile-register",
                        args=[
                            tenant_uuid,
                        ],
                    ),
                    method='post',
                    params={
                        'email': 'email',
                        'password': 'password',
                        'code': 'code',
                        'checkpassword': 'checkpassword',
                    },
                ),
            ),
        )
