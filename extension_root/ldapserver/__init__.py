"""
LDAP 插件处理
"""
from django.urls import reverse
from extension.models import Extension
from common.extension import InMemExtension
from runtime import Runtime
from config import get_app_config
from .constants import KEY
from .serializers import LdapServerSerializer


class LdapServerExtension(InMemExtension):
    """
    插件
    """

    def start(self, runtime: Runtime, *args, **kwargs):
        super().start(runtime=runtime, *args, **kwargs)

    def teardown(self, runtime: Runtime, *args, **kwargs):  # pylint: disable=unused-argument
        pass


extension = LdapServerExtension(
    tags='ldap',
    name="ldapserver",
    scope='tenant',
    type='tenant',
    description="LDAP SERVER",
    version="1.0",
    homepage="https://www.longguikeji.com",
    logo="",
    maintainer="guancyxx@guancyxx.cn",
    serializer=LdapServerSerializer
)
