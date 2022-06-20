from arkid.core.extension.auth_factor import AuthFactorExtension, BaseAuthFactorSchema
from .error import ErrorCode
from arkid.core.models import User
from arkid.common.sms import check_sms_code
from arkid.core import actions, pages
from .models import UserMobile
from pydantic import Field
from typing import List, Optional
from arkid.core.translation import gettext_default as _
from django.db import transaction
from arkid.core.extension import create_extension_schema
from .schema import *

package = "com.longgui.auth.factor.mobile"

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
        from api.v1.schema.user import UserCreateIn,UserItemOut,UserUpdateIn,UserListItemOut
        from api.v1.schema.mine import ProfileSchemaOut
        self.register_extend_api(
            AuthIn,
            UserCreateIn, UserItemOut, UserUpdateIn, UserListItemOut,
            mobile=str
        )
        self.register_extend_api(
            ProfileSchemaOut, 
            mobile=(Optional[str],Field(readonly=True))
        )
    
    def update_mine_mobile(self, request, tenant_id: str,data:UpdateMineMobileIn):
    
        return self.success()
    
    def authenticate(self, event, **kwargs):
        tenant = event.tenant
        request = event.request
        sms_code = request.POST.get('sms_code')
        mobile = request.POST.get('mobile')

        user_mobile = UserMobile.objects.filter(mobile=mobile).first()
        if user_mobile:
            if check_sms_code(mobile, sms_code):
                if user_mobile.user not in tenant.users.all():
                    msg = ErrorCode.USER_NOT_IN_TENANT_ERROR
                else:
                    return self.auth_success(user_mobile.user,event)
            else:
                msg = ErrorCode.SMS_CODE_MISMATCH
        else:
            msg = ErrorCode.MOBILE_NOT_EXISTS_ERROR
        return self.auth_failed(event, data=self.error(msg))

    @transaction.atomic()
    def register(self, event, **kwargs):
        tenant = event.tenant
        request = event.request
        mobile = request.POST.get('mobile')
        sms_code = request.POST.get('sms_code')

        config = self.get_current_config(event)
        ret, message = self.check_mobile_exists(mobile, config)
        if not ret:
            return self.error(message)
        
        if not check_sms_code(mobile, sms_code):
            return self.error(ErrorCode.SMS_CODE_MISMATCH)

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
            return False, ErrorCode.MOBILE_EMPTY

        if UserMobile.active_objects.filter(mobile=mobile).count():
            return False, ErrorCode.MOBILE_EXISTS_ERROR
        return True, None

    def _get_register_user(self, tenant, field_name, field_value):
        pass
    
    def create_auth_manage_page(self):
        
        mine_mobile_path = self.register_api(
            "/mine_mobile/",
            'POST',
            self.update_mine_mobile,
            tenant_path=True,
            response=UpdateMineMobileOut
        )
        
        name = '更改手机号码'

        page = pages.FormPage(name=name)
        page.create_actions(
            init_action=actions.ConfirmAction(
                path=mine_mobile_path
            ),
            global_actions={
                'confirm': actions.ConfirmAction(
                    path=mine_mobile_path
                ),
            }
        )
        return page


extension = MobileAuthFactorExtension(
    package=package,
    name="手机验证码认证因素",
    version='1.0',
    labels='auth_factor',
    homepage='https://www.longguikeji.com',
    logo='',
    author='guancyxx@guancyxx.cn',
)