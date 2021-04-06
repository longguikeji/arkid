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
    AppTypeProvider, StorageProvider,
)
from common.serializer import AppBaseSerializer, ExternalIdpBaseSerializer
from authorization_server.models import AuthorizationServer
from mfa.models import MFA
from common.exception import DuplicatedIdException

class Runtime:

    _instance = None

    sms_provider: SMSProvider = None
    cache_provider: CacheProvider = None
    storage_provider: StorageProvider = None

    external_idps: List
    external_idp_providers: Dict[str, ExternalIdpProvider]
    external_idp_serializers: Dict[str, ExternalIdpBaseSerializer]

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

            cls._instance.external_idps = []
            cls._instance.external_idp_providers = {}
            cls._instance.external_idp_serializers = {}

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

    def register_external_idp(self, key: str, name: str, description: str, provider: ExternalIdpProvider, serializer: ExternalIdpBaseSerializer=None):
        self.external_idps.append((key, name, description))
        if provider is not None:
            self.external_idp_providers[key] = provider

        if serializer is not None:
            self.external_idp_serializers[key] = serializer

    def register_mfa_provider(self, name: str, provider: MFAProvider):
        pass

    def register_authorization_server(self, id: str, name: str, description: str, provider: Optional[AuthorizationServerProvider]=None):
        for server in self.authorization_servers:
            if server.id == id:
                return # raise DuplicatedIdException(f'duplicated extension: {server.id} {server.name}')

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
        print('register_route:', namespace, urlpatterns)

    def register_storage_provider(self, provider: StorageProvider):
        self.storage_provider = provider
    
    def register_app_type(self, key: str, name: str, provider: AppTypeProvider, serializer: AppBaseSerializer) -> None:
        self.app_types.append((key, name))

        if provider is not None:
            self.app_type_providers[key] = provider

        if serializer is not None:
            self.app_type_serializers[key] = serializer

    @property
    def extension_serializers(self):
        from extension.utils import find_available_extensions
        extensions = find_available_extensions()
        data = {}
        for ext in extensions:
            if ext.serializer is not None:
                data[ext.name] = ext.serializer
        
        return data

def get_app_runtime() -> Runtime:
    o = Runtime()
    return o