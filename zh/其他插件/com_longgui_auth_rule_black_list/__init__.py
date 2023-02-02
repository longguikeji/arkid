import json
from typing import List, Optional

from ninja import Field, Schema
from arkid.core.api import operation
from arkid.core.event import AUTH_SUCCESS, BEFORE_USER_REGISTER
from arkid.core.extension import create_extension_schema
from arkid.core.extension.auth_rule import AuthRuleExtension, BaseAuthRuleSchema
from arkid.core.models import User
from arkid.core.translation import gettext_default as _
from arkid.core.constants import *
from .schema import *
from api.v1.pages.user_manage.user_list import page as user_list_page
from .errorcode import ErrorCode
import re


class AuthRuleBlackListExtension(AuthRuleExtension):

    def load(self):
        super().load()
        self.create_extension_config_schema()
        self.listen_event(AUTH_SUCCESS, self.auth_success)
        self.listen_event(BEFORE_USER_REGISTER, self.before_register)

    def create_extension_config_schema(self):
        AuthRuleBlackListConfigSchema = create_extension_schema(
            'AuthRuleBlackListConfigSchema',
            __file__,
            [
                (
                    'username__regex',
                    Optional[str],
                    Field(
                        title=_('username regex', '用户名正则'),
                        default='',
                    )
                ),
                (
                    'email__regex',
                    Optional[str],
                    Field(
                        title=_('email regex', '邮箱正则'),
                        default='',
                    )
                ),
                (
                    'mobile__regex',
                    Optional[str],
                    Field(
                        title=_('mobile regex', '电话号码正则'),
                        default='',
                    )
                ),
            ],
            base_schema=Schema
        )
        self.register_auth_rule_schema(
            AuthRuleBlackListConfigSchema,
            _("账号黑名单")
        )

    def auth_success(self, event, **kwargs):
        # 检查是否存在满足条件的配置
        user = event.data["user"]
        user_expanded = User.expand_objects.get(id=user.id)
        for config in self.get_tenant_configs(event.tenant):

            # 检查用户名规则
            if self.check_regex(user.username, config.config["username__regex"]):
                return self.rise_errorcode(
                    event,
                    ErrorCode.USERNAME_IN_BLACKLIST
                )

            if self.check_regex(user_expanded.get("mobile", None), config.config["mobile__regex"]):
                return self.rise_errorcode(
                    event,
                    ErrorCode.MOBILE_IN_BLACKLIST
                )

            if self.check_regex(user_expanded.get("email", None), config.config["email__regex"]):
                return self.rise_errorcode(
                    event,
                    ErrorCode.EMAIL_IN_BLACKLIST
                )

    def before_register(self, event, **kwargs):
        request_data = getattr(
            event.request,
            "data",
            None
        ) or json.loads(event.request.body)

        for config in self.get_tenant_configs(event.tenant):

            # 检查用户名规则
            if self.check_regex(request_data.get("username", None), config.config["username__regex"]):
                return self.rise_errorcode(
                    event,
                    ErrorCode.USERNAME_IN_BLACKLIST
                )

            if self.check_regex(request_data.get("mobile", None), config.config["mobile__regex"]):
                return self.rise_errorcode(
                    event,
                    ErrorCode.MOBILE_IN_BLACKLIST
                )

            if self.check_regex(request_data.get("email", None), config.config["email__regex"]):
                return self.rise_errorcode(
                    event,
                    ErrorCode.EMAIL_IN_BLACKLIST
                )

    def check_rule(self, event, config):
        pass

    def check_regex(self, obj: str, regex: str):
        if regex and obj:
            rs = re.fullmatch(regex, obj)
            if rs:
                return True
        return False


extension = AuthRuleBlackListExtension()
