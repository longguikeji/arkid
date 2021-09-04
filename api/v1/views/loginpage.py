from rest_framework import views
from ..serializers import loginpage as lp
from common import loginpage as model
from openapi.utils import extend_schema
from django.http.response import JsonResponse
from api.v1.views.tenant import TenantViewSet
from tenant.models import Tenant, TenantConfig
from config.models import PrivacyNotice
from external_idp.models import ExternalIdp
from api.v1.serializers.tenant import TenantExtendSerializer
from system.models import SystemConfig
from django.urls import reverse
from runtime import get_app_runtime
from login_register_config.models import LoginRegisterConfig

DEFAULT_LOGIN_REGISTER_EXTENSION = 'password_login_register'


@extend_schema(tags=['login page'])
class LoginPage(views.APIView):
    @extend_schema(responses=lp.LoginPagesSerializer)
    def get(self, request):
        tenant_uuid = request.query_params.get('tenant', None)
        tenant = Tenant.objects.filter(uuid=tenant_uuid).first()

        data = model.LoginPages()

        # 加载注册登录插件
        r = get_app_runtime()
        configs = LoginRegisterConfig.active_objects.filter(tenant=tenant)
        if not configs:
            config_data = {
                'username_login_enabled': True,
                'username_register_enabled': True,
            }
            config, _ = LoginRegisterConfig.objects.get_or_create(
                tenant=tenant, type=DEFAULT_LOGIN_REGISTER_EXTENSION, data=config_data
            )
            configs = [config]

        for config in configs:
            provider_cls = r.login_register_config_providers.get(config.type, None)
            assert provider_cls is not None

            config_data = config.data
            provider = provider_cls(config_data)
            self.add_login_form(data, provider, config.type, tenant_uuid)
            self.add_register_form(data, provider, config.type, tenant_uuid)
            self.add_reset_password_form(data, provider, config.type, tenant_uuid)

        if tenant:
            data.setTenant(TenantExtendSerializer(instance=tenant).data)

            # 登录表单增加第三方登录按钮
            self.add_tenant_idp_login_buttons(request, tenant, data)

        # 获取隐私声明
        agreement = self.get_privacy_notice(tenant)

        # 如果存在注册表单，登录表单下方添加跳转注册按钮, 注册表单下方增加跳转登录按钮
        self.add_login_register_button(data, agreement)

        # 如果存在登录表单，登录表单上增加忘记密码按钮
        self.add_reset_password_button(data, agreement)

        pages = lp.LoginPagesSerializer(data=data)
        pages.is_valid()
        return JsonResponse(pages.data)

    def append_extension_type_form_item(self, form, extension_type):
        items = form.get('items')
        items.append(
            model.LoginFormItem(type='hidden', name='extension', value=extension_type)
        )

    def add_login_form(self, data, provider, extension_type, tenant_uuid=None):
        form = provider.login_form
        if not form:
            return

        url = reverse('api:login')
        if tenant_uuid:
            url += '?tenant=tenant_uuid'
        if type(form) != list:
            forms = [form]
        else:
            forms = form

        for form in forms:
            form['submit'] = model.Button(
                label='登录', http=model.ButtonHttp(url=url, method='post')
            )

            self.append_extension_type_form_item(form, extension_type)
        data.addForm(model.LOGIN, form)

    def add_register_form(self, data, provider, extension_type, tenant_uuid=None):
        form = provider.register_form
        if not form:
            return

        url = reverse('api:register')
        if tenant_uuid:
            url += '?tenant=tenant_uuid'

        if type(form) != list:
            forms = [form]
        else:
            forms = form

        for form in forms:
            form['submit'] = model.Button(
                label='注册', http=model.ButtonHttp(url=url, method='post')
            )
            self.append_extension_type_form_item(form, extension_type)
        data.addForm(model.REGISTER, form)

    def add_reset_password_form(self, data, provider, extension_type, tenant_uuid=None):
        form = provider.reset_password_form
        if not form:
            return

        url = reverse('api:reset-password')
        if tenant_uuid:
            url += '?tenant=tenant_uuid'

        if type(form) != list:
            forms = [form]
        else:
            forms = form

        for form in forms:
            form['submit'] = model.Button(
                label='确认',
                http=model.ButtonHttp(url=url, method='post'),
                gopage=model.LOGIN,
            )

            self.append_extension_type_form_item(form, extension_type)
        data.addForm(model.PASSWORD, form)

    def get_privacy_notice(self, tenant):
        privacy_notice = PrivacyNotice.valid_objects.filter(
            tenant=tenant
        ).first()
        if privacy_notice and privacy_notice.is_active:
            agreement = {
                'title': privacy_notice.title,
                'content': privacy_notice.content,
            }
        else:
            agreement = {}
        return agreement

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
        if data.getPage(model.REGISTER) and data.getPage(model.LOGIN):
            if agreement:
                data.addBottom(
                    model.LOGIN,
                    model.Button(
                        prepend='还没有账号，',
                        label='立即注册',
                        gopage=model.REGISTER,
                        agreement=agreement,
                    ),
                )
            else:
                data.addBottom(
                    model.LOGIN,
                    model.Button(
                        prepend='还没有账号，',
                        label='立即注册',
                        gopage=model.REGISTER,
                    ),
                )
            data.addBottom(
                model.REGISTER,
                model.Button(prepend='已有账号，', label='立即登录', gopage=model.LOGIN),
            )
        return data

    def add_reset_password_button(self, data, agreement):
        if data.getPage(model.LOGIN) and data.getPage(model.PASSWORD):
            data.addBottom(model.LOGIN, model.Button(label='忘记密码', gopage='password'))
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
