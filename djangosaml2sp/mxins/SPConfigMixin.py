"""
SP 配置混入类
"""
from django.http import HttpRequest
from saml2.config import SPConfig
from djangosaml2sp.cache import StateCache, IdentityCache
from djangosaml2sp.overrides import Saml2Client
from djangosaml2sp.sp import SP


class SPConfigViewMixin:
    """ Mixin for some of the SAML views with re-usable methods.
    """

    def get_sp_config(self, tenant_uuid) -> SPConfig:
        """
        获取SP 配置
        """
        conf = SPConfig()
        return conf.load(SP.construct_metadata(tenant_uuid))

    def get_state_client(self, tenant_uuid, request: HttpRequest):
        """
        获取client
        """
        conf = self.get_sp_config(tenant_uuid)
        state = StateCache(request.saml_session)
        client = Saml2Client(
            conf,
            state_cache=state,
            identity_cache=IdentityCache(request.saml_session)
        )
        return state, client
