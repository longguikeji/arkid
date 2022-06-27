from arkid.core.extension import create_extension_schema
from arkid.core.extension.auth_rule import AuthRuleExtension, BaseAuthRuleSchema
from arkid.core.translation import gettext_default as _
from ninja import Schema
from pydantic import Field


AuthRuleRetryTimesConfigSchema = create_extension_schema(
    'AuthRuleRetryTimesConfigSchema',
    __file__,
    [
        ('try_times', str, Field(title=_('try_times', '限制重试次数'))),
        ('verify_code_digits', str, Field(title=_('verify_code_digits', '验证码位数'))),
    ],
    base_schema=BaseAuthRuleSchema
)


class AuthRuleRetryTimesExtension(AuthRuleExtension):

    def load(self):
        super().load()

        self.register_auth_rule_schema(
            AuthRuleRetryTimesConfigSchema,
            "retry_times"
        )

    def before_auth(self, event, **kwargs):
        
        pass

    def auth_success(self, event, **kwargs):
        pass

    def auth_fail(self, event, **kwargs):
        pass


extension = AuthRuleRetryTimesExtension()
