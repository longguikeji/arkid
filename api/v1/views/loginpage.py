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

            # 添加 tenant的登录注册表单
            self.add_tenant_login_register_form(request, tenant, data)

            # 登录表单增加第三方登录按钮
            self.add_tenant_idp_login_buttons(request, tenant, data)

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

        # 获取隐私声明
        agreement = self.get_privacy_notice(tenant)

        # 如果存在注册表单，登录表单下方添加跳转注册按钮, 注册表单下方增加跳转登录按钮
        self.add_login_register_button(data, agreement)

        # 如果存在登录表单，登录表单上增加忘记密码按钮
        self.add_reset_password_button(data, agreement)

        pages = lp.LoginPagesSerializer(data=data)
        pages.is_valid()
        return JsonResponse(pages.data)

    def get_privacy_notice(self, tenant):
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
        return agreement

    def add_tenant_login_register_form(self, request, tenant, data):
        tenant_config = TenantConfig.objects.filter(
            is_del=False,
            tenant=tenant,
        ).first()
        if tenant_config:
            field_names = tenant_config.data.get(
                'native_login_register_field_names'
            ) or [
                'mobile',
                'email',
            ]
        else:
            field_names = ['mobile', 'email']

        if 'mobile' in field_names:
            data.addForm(model.LOGIN, TenantViewSet().mobile_login_form(tenant.uuid))

        # 除了mobile用验证码登录，其他字段包括email用密码登录
        field_names.remove('mobile')

        field_uuids = tenant_config.data.get('custom_login_register_field_uuids', [])
        # 除了mobile之外的原生字段，和自定义字段共用一个登录窗口, 用密码登录
        if field_names or field_uuids:
            data.addForm(
                model.LOGIN,
                TenantViewSet().secret_login_form(
                    request, tenant.uuid, field_names, field_uuids
                ),
            )
        for field_name in field_names:
            data.addForm(
                model.REGISTER,
                TenantViewSet().native_field_register_form(tenant.uuid, field_name),
            )
        # 自定义字段的注册表单
        for uuid in field_uuids:
            data.addForm(
                model.REGISTER,
                TenantViewSet().custom_field_register_form(tenant.uuid, uuid),
            )

        return data

    def add_tenant_idp_login_buttons(self, request, tenant, data):
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
        if data.getPage(model.LOGIN) and data.getPage(model.LOGIN).get('extend', None):
            data.setExtendTitle(model.LOGIN, '第三方登录')
        return data

    def add_login_register_button(self, data, agreement):
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
        return data

    def add_reset_password_button(self, data, agreement):
        if data.getPage(model.LOGIN):
            data.addBottom(model.LOGIN, model.Button(label='忘记密码', gopage='password'))
            data.addForm(model.PASSWORD, self.mobile_password_reset_form())
            data.addForm(model.PASSWORD, self.email_password_reset_form())
            if data.getPage(model.REGISTER):
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
        return data

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
                    append=model.Button(
                        label='发送验证码',
                        delay=60,
                        http=model.ButtonHttp(
                            url=reverse('api:sms', args=['reset_password']),
                            method='post',
                            params={'mobile': 'mobile'},
                        ),
                    ),
                ),
                model.LoginFormItem(
                    type='text',
                    name='code',
                    placeholder='验证码',
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
            ],
            submit=model.Button(
                label='确认',
                http=model.ButtonHttp(
                    url=reverse(
                        "api:user-mobile-reset-password",
                    ),
                    method='post',
                    params={
                        'mobile': 'mobile',
                        'password': 'password',
                        'code': 'code',
                        'checkpassword': 'checkpassword',
                    },
                ),
                gopage=model.LOGIN,
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
                    placeholder='邮箱账号',
                    append=model.Button(
                        label='发送验证码',
                        delay=60,
                        http=model.ButtonHttp(
                            url=reverse('api:email', args=['reset_password'])
                            + '?send_verify_code=true',
                            method='post',
                            params={'email': 'email'},
                        ),
                    ),
                ),
                model.LoginFormItem(
                    type='text',
                    name='code',
                    placeholder='验证码',
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
            ],
            submit=model.Button(
                label='确认',
                http=model.ButtonHttp(
                    url=reverse(
                        "api:user-email-reset-password",
                    ),
                    method='post',
                    params={
                        'email': 'email',
                        'password': 'password',
                        'code': 'code',
                        'checkpassword': 'checkpassword',
                    },
                ),
                gopage=model.LOGIN,
            ),
        )
