from django.http import HttpRequest
from saml2.config import SPConfig
from djangosaml2sp.conf import get_config
from djangosaml2sp.cache import StateCache,IdentityCache
from djangosaml2sp.overrides import Saml2Client

class SPConfigMixin:
    """ Mixin for some of the SAML views with re-usable methods.
    """

    config_loader_path = None

    def get_config_loader_path(self, request: HttpRequest):
        return self.config_loader_path

    def get_sp_config(self, request: HttpRequest) -> SPConfig:
        return get_config(self.get_config_loader_path(request), request)

    def get_state_client(self, request: HttpRequest):
        conf = self.get_sp_config(request)
        state = StateCache(request.saml_session)
        client = Saml2Client(
            conf,
            state_cache=state,
            identity_cache=IdentityCache(request.saml_session)
        )
        return state, client
