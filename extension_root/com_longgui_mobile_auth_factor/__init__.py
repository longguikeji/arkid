from arkid.core.extension.auth_factor import AuthFactorExtension, BaseAuthFactorSchema
from arkid.core.error import ErrorCode
from arkid.core.models import User
from arkid.common.sms import check_sms_code
from arkid.core import actions, pages
from .models import UserMobile
from pydantic import Field
from typing import List, Optional
from arkid.core.translation import gettext_default as _
from django.db import transaction
from arkid.core.extension import create_extension_schema

package = "com.longgui.mobile_auth_factor"

MobileAuthFactorSchema = create_extension_schema('MobileAuthFactorSchema',package, 
        [
            ('template_code', str , Field(title=_('template_code', '短信模板ID'))),
            ('sign_name', str , Field(title=_('sign_name', 'sign_name'))),
            ('sms_up_extend_code', str , Field(title=_('sms_up_extend_code', 'sms_up_extend_code'))),
        ],
        BaseAuthFactorSchema,
    )

class MobileAuthFactorExtension(AuthFactorExtension):
    def load(self):
        super().load()
        self.register_extend_field(UserMobile, "mobile")
        self.register_auth_factor_schema(MobileAuthFactorSchema, 'mobile')
        from api.v1.schema.auth import AuthIn
        self.register_extend_api(AuthIn, mobile=str)
        
    def authenticate(self, event, **kwargs):
        tenant = event.tenant
        request = event.request
        sms_code = request.POST.get('sms_code')
        mobile = request.POST.get('mobile')

        user_mobile = UserMobile.objects.filter(mobile=mobile).first()
        if user_mobile:
            if check_sms_code(mobile, sms_code):
                if user_mobile.user not in tenant.users.all():
                    error_code = ErrorCode.USER_NOT_IN_TENANT_ERROR.value
                    message = _('Can not find user in tenant',"该租户下未找到对应用户。")
                else:
                    return self.auth_success(user_mobile.user,event)
            else:
                error_code = ErrorCode.SMS_CODE_MISMATCH.value
                message = _('sms code mismatched',"手机验证码错误")
        else:
            error_code = ErrorCode.MOBILE_NOT_EXISTS_ERROR.value
            message = _('mobile is not exists',"电话号码不存在")
        return self.auth_failed(event, data={'error': error_code, 'message': message})

    @transaction.atomic()
    def register(self, event, **kwargs):
        tenant = event.tenant
        request = event.request
        mobile = request.POST.get('mobile')
        sms_code = request.POST.get('sms_code')

        config = self.get_current_config(event)
        ret, message = self.check_mobile_exists(mobile, config)
        if not ret:
            data = {
                'error': ErrorCode.MOBILE_ERROR.value,
                'message': message,
            }
            return data
        
        if not check_sms_code(mobile, sms_code):
            data = {
                'error': ErrorCode.SMS_CODE_MISMATCH.value,
                'message': _("sms code mismatched","手机验证码错误")
            }
            return data

        # user = User.objects.create(tenant=tenant)
        user = User(tenant=tenant)
        mobile = UserMobile(user=user,mobile=mobile)
        user.save()
        mobile.save()
        tenant.users.add(user)
        tenant.save()

        return user

    def reset_password(self, event, **kwargs):
        pass

    def create_login_page(self, event, config):
        items = [
            {
                "type": "text",
                "name": "phone_number",
                "placeholder": "手机号码",
                "append": {
                    "title": "发送验证码",
                    "http": {
                        "url": "/api/v1/tenant/{tenant_id}/send_sms_code/",
                        "method": "post",
                        "params": {
                            "phone_number": "phone_number",
                            "config_id": "config_id"
                        },
                        "payload": {
                            "auth_code_length": 6
                        }
                    },
                    "delay": 60
                }
            },
            {
                "type": "text",
                "name": "sms_code",
                "placeholder": "验证码",
            },
        ]
        self.add_page_form(config, self.LOGIN, "手机验证码登录", items)

    def create_register_page(self, event, config):
        items = [
            {
                "type": "text",
                "name": "phone_number",
                "placeholder": "手机号码",
                "append": {
                    "title": "发送验证码",
                    "http": {
                        "url": "/api/v1/tenant/{tenant_id}/send_sms_code/",
                        "method": "post",
                        "params": {
                            "phone_number": "phone_number",
                            "config_id": "config_id"
                        },
                        "payload": {
                            "auth_code_length": 6
                        }
                    },
                    "delay": 60
                }
            },
            {
                "type": "text",
                "name": "sms_code",
                "placeholder": "验证码"
            },
        ]
        self.add_page_form(config, self.REGISTER, "手机验证码注册", items)

    def create_password_page(self, event, config):
        items = [
            {
                "type": "text",
                "name": "phone_number",
                "placeholder": "手机号码",
                "append": {
                    "title": "发送验证码",
                    "http": {
                        "url": "/api/v1/tenant/{tenant_id}/send_sms_code/",
                        "method": "post",
                        "params": {
                            "phone_number": "phone_number",
                            "config_id": "config_id"
                        },
                        "payload": {
                            "auth_code_length": 6
                        }
                    },
                    "delay": 60
                }
            },
            {
                "type": "text",
                "name": "sms_code",
                "placeholder": "验证码"
            },
            {
                "type": "password",
                "name": "password",
                "placeholder": "密码"
            },
            {
                "type": "password",
                "name": "checkpassword",
                "placeholder": "密码确认"
            },
        ]
        self.add_page_form(config, self.RESET_PASSWORD, "手机验证码重置密码", items)

    def create_other_page(self, event, config):
        pass
    
    def check_mobile_exists(self, mobile, config):
        if not mobile:
            return False, _('No mobile provide',"手机号码不能为空")

        if UserMobile.active_objects.filter(mobile=mobile).count():
            return False, _('Mobile is already exists',"手机号码已存在")
        return True, None

    def _get_register_user(self, tenant, field_name, field_value):
        pass
    
    def create_auth_manage_page(self):
        name = '更改手机号码'

        page = pages.FormPage(name=name)
        
        pages.register_front_pages(page)

        page.create_actions(
            init_action=actions.DirectAction(
                path='/api/v1/platform_config/',
                method=actions.FrontActionMethod.GET,
            ),
            global_actions={
                'confirm': actions.ConfirmAction(
                    path="/api/v1/platform_config/"
                ),
            }
        )
        return page


extension = MobileAuthFactorExtension(
    package=package,
    name="手机验证码认证",
    version='1.0',
    labels='auth_factor',
    homepage='https://www.longguikeji.com',
    logo='',
    author='guancyxx@guancyxx.cn',
)