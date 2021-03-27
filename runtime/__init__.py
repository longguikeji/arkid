from typing import (
    Optional, List, Dict, TypeVar, Generic
)
from collections import OrderedDict
from common.provider import (
    SMSProvider,
    CacheProvider,
    ExternalIdpProvider,
    MFAProvider,
    AuthorizationServerProvider,
    AppTypeProvider,
)
from common.serializer import AppBaseSerializer
from external_idp.models import ExternalIdp
from authorization_server.models import AuthorizationServer
from mfa.models import MFA
from common.exception import DuplicatedIdException

class Runtime:

    _instance = None

    sms_provider: SMSProvider = None
    cache_provider: CacheProvider = None
    external_idps: List[ExternalIdp] = []
    authorization_servers: List[AuthorizationServer] = []

    mfa_providers: Optional[List] = None
    app_types: List
    app_type_providers: Dict[str, AppTypeProvider]
    app_type_serializers: Dict[str, AppBaseSerializer]

    urlpatterns: Dict = {}

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kwargs)
            cls._instance.urlpatterns = OrderedDict()
            cls._instance.app_types = []
            cls._instance.app_type_providers = {}
            cls._instance.app_type_serializers = {}

        return cls._instance

    def register_task(self):
        '''
        register background task
        '''
        pass

    def register_config(self, name: str, key: str):
        '''
        register config section
        '''
        pass

    def register_external_idp(self, id: str, name: str, description: str, provider: ExternalIdpProvider):
        for idp in self.external_idps:
            if idp.id == id:
                raise DuplicatedIdException(f'duplicated extension: {idp.id} {idp.name}')

        idp = ExternalIdp(
            id=id, 
            name=name, 
            description=description,
            provider=provider, 
            source=None,
        )
        self.external_idps.append(idp)

    def register_mfa_provider(self, name: str, provider: MFAProvider):
        pass

    def register_authorization_server(self, id: str, name: str, description: str, provider: Optional[AuthorizationServerProvider]=None):
        for server in self.authorization_servers:
            if server.id == id:
                raise DuplicatedIdException(f'duplicated extension: {server.id} {server.name}')

        server = AuthorizationServer(
            id=id, 
            name=name, 
            description=description,
            provider=provider, 
        )
        self.authorization_servers.append(server)

    def register_route(self, urlpatterns: List, namespace: str='global') -> any:
        assert namespace in ['global', 'tenant', 'local']
        self.urlpatterns.setdefault(namespace, [])
        self.urlpatterns[namespace] += urlpatterns

    def register_storage_provider(self):
        pass
    
    def register_app_type(self, key: str, name: str, provider: AppTypeProvider, serializer: AppBaseSerializer) -> None:
        self.app_types.append((key, name))

        if provider is not None:
            self.app_type_providers[key] = provider

        if serializer is not None:
            self.app_type_serializers[key] = serializer


def get_app_runtime() -> Runtime:
    o = Runtime()
    return o