"""
插件处理
"""
from common.extension import InMemExtension
from runtime import Runtime
from .serializers import FirstLoginRuleSerializer
from .providers import FirstLoginRuleProvider

class AuthRulesExtension(InMemExtension):
    """
    认证规则插件
    """

    def start(self, runtime: Runtime, *args, **kwargs):

        runtime.register_auth_rule_type(
            key="ARC0001",
            name="首次登陆",
            provider=FirstLoginRuleProvider,
            serializer=FirstLoginRuleSerializer
        )

        super().start(runtime=runtime, *args, **kwargs)

    def teardown(self, runtime: Runtime, *args, **kwargs): # pylint: disable=unused-argument
        runtime.logout_auth_rule_type(
            key="ARC0001",
            name="首次登陆",
            provider=FirstLoginRuleProvider,
            serializer=FirstLoginRuleSerializer
        )


extension = AuthRulesExtension(
    tags='auth_rules_example',
    name="auth_rules_example",
    scope='tenant',
    type='tenant',
    description="基础认证规则",
    version="2.0",
    homepage="https://www.longguikeji.com",
    logo="",
    maintainer="北京龙归科技有限公司",
)
