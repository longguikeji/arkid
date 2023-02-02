import json
from arkid.core.extension.auth_factor import AuthFactorExtension, BaseAuthFactorSchema
from arkid.core.schema import ResponseSchema
from arkid.core.api import GlobalAuth, operation
from arkid.core.models import Tenant, User
from arkid.core import pages, actions
from arkid.extension.models import TenantExtensionConfig
from pydantic import Field
from typing import List, Optional
from arkid.core.translation import gettext_default as _
from django.db import transaction
from arkid.core.extension import create_extension_schema
from enum import Enum
from pathlib import Path
from django.http import HttpResponse, Http404, JsonResponse
from arkid.core.token import refresh_token
from arkid.core.models import Tenant, User
from arkid.core.error import ErrorCode, ErrorDict
from arkid.core.constants import *
from arkid.core.event import BEFORE_REFRESH_TOKEN
from arkid.common.logger import logger
from .schema import (
    AuthenticatorsItemOut,
    AuthenticatorDeleteOut,
    UserOTPAuthenticatorSchema,
    UserOTPAuthenticatorOut,
    UserOTPAuthenticatorEditOut,
    UserOTPAuthenticatorEditSchema,
)
from .models import OTPUser
from .error import OTPErrorCode
import pyotp
from arkid.core.schema import ResponseSchema
from arkid.core import event as core_event

OTPAuthFactorSchema = create_extension_schema(
    "OTPAuthFactorSchema",
    __file__,
    [
        (
            'register_enabled',
            bool,
            Field(
                default=False,
                title=_('register_enabled', '启用注册'),
                readonly=True,
                hidden=True,
            ),
        ),
        (
            "reset_password_enabled",
            bool,
            Field(
                default=False,
                title=_("reset_password_enabled", "启用重置密码"),
                readonly=True,
                hidden=True,
            ),
        ),
    ],
    BaseAuthFactorSchema,
)


class OTPAuthFactorExtension(AuthFactorExtension):
    def load(self):
        super().load()
        self.register_auth_factor_schema(OTPAuthFactorSchema, "OTP")
        self.listen_event(BEFORE_REFRESH_TOKEN, self.before_refresh_token_event)

    def before_refresh_token_event(self, event, **kwargs):
        tenant = event.tenant
        request = event.request
        configs = self.get_tenant_configs(tenant)
        login_enabled = False
        user = event.data.get('user')
        for config in configs:
            if config.config.get('login_enabled'):
                login_enabled = True
                break

        if not login_enabled:
            return

        otp_user = OTPUser.objects.filter(target=user).first()
        if not otp_user:
            return
        if not otp_user.is_apply:
            return

        payload = request.POST or json.load(request.body)
        otpcode = payload.get('otpcode')
        if not otpcode:
            data = {
                'error': ErrorCode.OTP_2FA_REQUIRED.value[0],
                'message': '用户需要OTP验证',
                'package': self.package,
                'data': {
                    'form': {
                        'items': [
                            {
                                "type": "text",
                                "name": "otpcode",
                                "placeholder": "一次性密码",
                            },
                        ],
                    }
                },
            }
            # core_event.remove_event_id(event)
            core_event.break_event_loop(data)
        else:
            # 校验otpcode
            totp = pyotp.parse_uri(otp_user.otp_uri)
            res = totp.verify(otpcode)
            if res:
                return
            else:
                data = {
                    'error': OTPErrorCode.OTP_CODE_MISMATCH_ERROR.value[0],
                    'message': 'OTP代码不一致',
                }
            # core_event.remove_event_id(event)
            core_event.break_event_loop(data)

    def check_auth_data(self, event, **kwargs):
        pass

    def fix_login_page(self, event, **kwargs):
        pass

    def authenticate(self, event, **kwargs):
        pass

    @transaction.atomic()
    def register(self, event, **kwargs):
        pass

    def reset_password(self, event, **kwargs):
        pass

    def create_login_page(self, event, config, config_data):
        pass

    def create_register_page(self, event, config, config_data):
        pass

    def create_password_page(self, event, config, config_data):
        pass

    def create_other_page(self, event, config, config_data):
        pass

    def create_auth_manage_page(self):
        pass

    @operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN, NORMAL_USER])
    def get_mine_otp_authenticators(self, request, tenant_id: str):
        user = request.user
        otp_user = OTPUser.objects.filter(target=user)
        return otp_user

    @operation(
        AuthenticatorDeleteOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN, NORMAL_USER]
    )
    def delete_mine_otp_authenticator(self, request, tenant_id: str, id: str):
        otp_user = OTPUser.objects.filter(id=id).first()
        if otp_user:
            otp_user.kill()
        return self.error(ErrorCode.OK)

    @operation(
        AuthenticatorDeleteOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN, NORMAL_USER]
    )
    def edit_mine_otp_authenticator(
        self, request, tenant_id: str, id: str, data: UserOTPAuthenticatorEditSchema
    ):
        otp_user = OTPUser.objects.filter(id=id).first()
        if otp_user:
            otp_user.is_apply = data.is_apply
            otp_user.save()
        return self.error(ErrorCode.OK)

    @operation(
        UserOTPAuthenticatorEditOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN, NORMAL_USER]
    )
    def get_mine_otp_authenticator_item(self, request, tenant_id: str, id: str):
        otp_user = OTPUser.objects.filter(id=id).first()
        return {'data': otp_user}

    @operation(
        UserOTPAuthenticatorSchema, roles=[TENANT_ADMIN, PLATFORM_ADMIN, NORMAL_USER]
    )
    def set_mine_otp_authenticator(
        self, request, tenant_id: str, data: UserOTPAuthenticatorSchema
    ):

        user = request.user
        otp_uri = data.otp_uri
        otp_code = data.otp_code
        if not otp_code:
            return self.error(OTPErrorCode.NONE_OTP_CODE_ERROR)

        totp = pyotp.parse_uri(otp_uri)
        res = totp.verify(otp_code)
        if res:
            otp_user = OTPUser.objects.filter(target=user).first()
            if otp_user:
                otp_user.kill()
            OTPUser.valid_objects.create(target=user, otp_uri=otp_uri, is_apply=True)
            return self.error(ErrorCode.OK)
        else:
            return self.error(OTPErrorCode.OTP_CODE_MISMATCH_ERROR)

    @operation(
        UserOTPAuthenticatorOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN, NORMAL_USER]
    )
    def get_mine_otp_authenticator(self, request, tenant_id: str):
        user = request.user
        secret = pyotp.random_base32()

        uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user.username, issuer_name='ArkID'
        )
        return {'data': {'otp_uri': uri, 'otp_code': ''}}

    def register_auth_manage_page(self):
        # 设置OTP认证器

        get_mine_otp_authenticators_path = self.register_api(
            "/mine_otp_authenticators/",
            'GET',
            self.get_mine_otp_authenticators,
            tenant_path=True,
            response=List[AuthenticatorsItemOut],
        )
        delete_mine_otp_authenticator_path = self.register_api(
            "/mine_otp_authenticators/{id}",
            'DELETE',
            self.delete_mine_otp_authenticator,
            tenant_path=True,
            response=AuthenticatorDeleteOut,
        )
        edit_mine_otp_authenticator_path = self.register_api(
            "/mine_otp_authenticators/{id}",
            'PUT',
            self.edit_mine_otp_authenticator,
            tenant_path=True,
            response=AuthenticatorDeleteOut,
        )
        get_mine_otp_authenticator_item_path = self.register_api(
            "/mine_otp_authenticators/{id}",
            'GET',
            self.get_mine_otp_authenticator_item,
            tenant_path=True,
            response=UserOTPAuthenticatorEditOut,
        )

        set_mine_otp_authenticator_path = self.register_api(
            "/mine_otp_authenticator/",
            'POST',
            self.set_mine_otp_authenticator,
            tenant_path=True,
            response=ResponseSchema,
        )
        get_mine_otp_authenticator_path = self.register_api(
            "/mine_otp_authenticator/",
            'GET',
            self.get_mine_otp_authenticator,
            tenant_path=True,
            response=UserOTPAuthenticatorOut,
        )

        form_page = pages.FormPage(name='设置OTP身份验证器')
        form_page.create_actions(
            init_action=actions.DirectAction(
                path=get_mine_otp_authenticator_path,
                method=actions.FrontActionMethod.GET,
            ),
            global_actions={
                'confirm': actions.ConfirmAction(
                    path=set_mine_otp_authenticator_path,
                    method=actions.FrontActionMethod.POST,
                ),
            },
        )

        edit_page = pages.FormPage(name='编辑OTP身份验证器')
        edit_page.create_actions(
            init_action=actions.DirectAction(
                path=get_mine_otp_authenticator_item_path,
                method=actions.FrontActionMethod.GET,
            ),
            global_actions={
                'confirm': actions.ConfirmAction(
                    path=edit_mine_otp_authenticator_path,
                    method=actions.FrontActionMethod.PUT,
                ),
            },
        )

        table_page = pages.TablePage(name='OTP身份验证器')
        table_page.create_actions(
            init_action=actions.DirectAction(
                path=get_mine_otp_authenticators_path,
                method=actions.FrontActionMethod.GET,
            ),
            local_actions={
                "edit": actions.OpenAction(name='编辑', page=edit_page),
                "delete": actions.DirectAction(
                    name='删除',
                    path=delete_mine_otp_authenticator_path,
                    method=actions.FrontActionMethod.DELETE,
                ),
            },
            global_actions={
                'set_otp': actions.OpenAction(
                    page=form_page,
                    name=_('Set OTP Authenticator', '设置OTP身份验证器'),
                ),
            },
        )
        from api.v1.pages.mine.auth_manage import page as auth_manage_page

        self.register_front_pages([form_page, edit_page, table_page])
        auth_manage_page.add_pages(table_page)


extension = OTPAuthFactorExtension()
