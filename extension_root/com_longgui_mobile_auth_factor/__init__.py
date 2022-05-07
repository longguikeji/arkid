from distutils import core
import re
from tabnanny import check
from arkid.core.extension.auth_factor import AuthFactorExtension, BaseAuthFactorSchema
from arkid.core.error import ErrorCode
from arkid.core.models import User
from arkid.common.sms import check_sms_code
from .models import UserMobile
from pydantic import Field
from typing import List, Optional
from arkid.core.translation import gettext_default as _
from django.db import transaction
from arkid.core.extension import create_extension_schema

package = "com.longgui.mobile_auth_factor"

MobileAuthFactorSchema = create_extension_schema('MobileAuthFactorSchema',package, 
        [
            ('reset_password_enabled', Optional[bool] , Field(deprecated=True)),
            ('login_enabled_field_names', List[str],
                Field(
                    default=[], 
                    title=_('login_enabled_field_names', '启用电话号码登录的字段'),
                    url='/api/v1/login_fields?tenant={tenant_id}'
                )
            ),
            ('register_enabled_field_names', List[str],
                Field(
                    default=[], 
                    title=_('register_enabled_field_names', '启用电话号码注册的字段'),
                    url='/api/v1/register_fields?tenant={tenant_id}'
                )
            ),
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
                    return self.auth_success(user_mobile.user)
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
                'message': _("sms code mismatched","收集验证码错误")
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
                "name": "mobile",
                "placeholder": "手机号码"
            },
            {
                "type": "text",
                "name": "sms_code",
                "placeholder": "验证码"
            },
        ]
        self.add_page_form(config, self.LOGIN, "手机验证码登录", items)

    def create_register_page(self, event, config):
        items = [
            {
                "type": "text",
                "name": "mobile",
                "placeholder": "手机号码"
            },
            {
                "type": "text",
                "name": "sms_code",
                "placeholder": "验证码"
            },
        ]
        self.add_page_form(config, self.REGISTER, "手机验证码注册", items)

    def create_password_page(self, event, config):
        pass

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


extension = MobileAuthFactorExtension(
    package=package,
    description="Mobile 认证因素",
    version='1.0',
    labels='auth_factor',
    homepage='https://www.longguikeji.com',
    logo='',
    author='guancyxx@guancyxx.cn',
)