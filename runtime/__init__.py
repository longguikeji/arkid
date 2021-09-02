from typing import Optional, List, Dict, TypeVar, Generic
from collections import OrderedDict
from common.provider import (
    BaseAuthRuleProvider,
    SMSProvider,
    CacheProvider,
    ExternalIdpProvider,
    MFAProvider,
    AuthorizationServerProvider,
    AppTypeProvider,
    StorageProvider,
    MigrationProvider,
    AuthCodeProvider,
    TenantUserConfigProvider,
    LoginRegisterConfigProvider,
)
from common.serializer import (
    AppBaseSerializer,
    AuthRuleBaseSerializer,
    ExternalIdpBaseSerializer,
    LoginRegisterConfigBaseSerializer,
)
from authorization_server.models import AuthorizationServer
from mfa.models import MFA
from common.exception import DuplicatedIdException

class Runtime:

    _instance = None

    sms_provider: SMSProvider = None
    cache_provider: CacheProvider = None
    storage_provider: StorageProvider = None
    authcode_provider: AuthCodeProvider = None
    tenantuserconfig_provider: TenantUserConfigProvider = None
    migration_provider: MigrationProvider = None

    external_idps: List
    external_idp_providers: Dict[str, ExternalIdpProvider]
    external_idp_serializers: Dict[str, ExternalIdpBaseSerializer]

    login_register_configs: List
    login_register_config_providers: Dict[str, LoginRegisterConfigProvider]
    login_register_config_serializers: Dict[str, LoginRegisterConfigBaseSerializer]

    authorization_servers: List[AuthorizationServer] = []

    mfa_providers: Optional[List] = None

    app_types: List
    app_type_providers: Dict[str, AppTypeProvider]
    app_type_serializers: Dict[str, AppBaseSerializer]

    auth_rule_types: List
    auth_rule_type_providers: Dict[str, BaseAuthRuleProvider]
    auth_rule_type_serializers: Dict[str, AuthRuleBaseSerializer]

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

            cls._instance.login_register_configs = []
            cls._instance.login_register_config_providers = {}
            cls._instance.login_register_config_serializers = {}

            cls._instance.auth_rule_types = []
            cls._instance.auth_rule_type_providers = {}
            cls._instance.auth_rule_type_serializers = {}

        return cls._instance

    def quit_all_extension(self):
        '''
        quit all extension
        '''
        self.urlpatterns = OrderedDict()
        self.app_types = []
        self.app_type_providers = {}
        self.app_type_serializers = {}
        self.external_idps = []
        self.external_idp_providers = {}
        self.external_idp_serializers = {}
        self.login_register_configs = []
        self.login_register_config_providers = {}
        self.login_register_config_serializers = {}
        self.authorization_servers = []
        self.sms_provider = None
        self.cache_provider = None
        self.storage_provider = None
        self.authcode_provider = None
        self.migration_provider = None

        self.auth_rule_types = []
        self.auth_rule_type_providers = {}
        self.auth_rule_type_serializers = {}

    def register_task(self):
        """
        register background task
        """
        pass

    def register_config(self, name: str, key: str):
        """
        register config section
        """
        pass

    def register_external_idp(
        self,
        key: str,
        name: str,
        description: str,
        provider: ExternalIdpProvider,
        serializer: ExternalIdpBaseSerializer = None,
    ):
        if (key, name, description) not in self.external_idps:
            self.external_idps.append((key, name, description))
        if provider is not None:
            self.external_idp_providers[key] = provider

        if serializer is not None:
            self.external_idp_serializers[key] = serializer

    def logout_external_idp(
        self,
        key: str,
        name: str,
        description: str,
        provider: ExternalIdpProvider,
        serializer: ExternalIdpBaseSerializer = None,
    ):
        if (key, name, description) in self.external_idps:
            self.external_idps.remove((key, name, description))
        if provider is not None and key in self.external_idp_providers:
            self.external_idp_providers.pop(key)
        if serializer is not None and key in self.external_idp_serializers:
            self.external_idp_serializers.pop(key)
        print('logout_external_idp:', name)

    def register_login_register_config(
        self,
        key: str,
        name: str,
        description: str,
        provider: LoginRegisterConfigProvider,
        serializer: LoginRegisterConfigBaseSerializer = None,
    ):
        if (key, name, description) not in self.login_register_configs:
            self.login_register_configs.append((key, name, description))
        if provider is not None:
            self.login_register_config_providers[key] = provider

        if serializer is not None:
            self.login_register_config_serializers[key] = serializer

    def logout_login_register_config(
        self,
        key: str,
        name: str,
        description: str,
        provider: LoginRegisterConfigProvider,
        serializer: LoginRegisterConfigBaseSerializer = None,
    ):
        if (key, name, description) in self.login_register_configs:
            self.login_register_configs.remove((key, name, description))
        if provider is not None and key in self.login_register_config_providers:
            self.login_register_config_providers.pop(key)
        if serializer is not None and key in self.login_register_config_serializers:
            self.login_register_config_serializers.pop(key)
        print('logout_login_register_config:', name)

    def register_mfa_provider(self, name: str, provider: MFAProvider):
        pass

    def register_authorization_server(
        self,
        id: str,
        name: str,
        description: str,
        provider: Optional[AuthorizationServerProvider] = None,
    ):
        for server in self.authorization_servers:
            if server.id == id:
                return  # raise DuplicatedIdException(f'duplicated extension: {server.id} {server.name}')

        server = AuthorizationServer(
            id=id,
            name=name,
            description=description,
            provider=provider,
        )
        self.authorization_servers.append(server)

    def logout_authorization_server(
        self,
        id: str,
        name: str,
        description: str,
        provider: Optional[AuthorizationServerProvider] = None,
    ):
        for server in self.authorization_servers:
            if server.id == id:
                self.authorization_servers.remove(server)
        print('logout_authorization_server:', name)

    def register_route(self, urlpatterns: List, namespace: str = 'global') -> any:
        assert namespace in ['global', 'tenant', 'local']
        self.urlpatterns.setdefault(namespace, [])
        self.urlpatterns[namespace] += urlpatterns
        print('register_route:', namespace, urlpatterns)

    def logout_route(self, urlpatterns: List, namespace: str = 'global') -> any:
        assert namespace in ['global', 'tenant', 'local']
        self.urlpatterns.setdefault(namespace, [])
        values = self.urlpatterns[namespace]
        for item in urlpatterns:
            flag = False
            index = 0
            for i, check_item in enumerate(values):
                if check_item.namespace == item.namespace:
                    flag = True
                    index = i
                    break
            if flag is True:
                values.pop(index)
        self.urlpatterns[namespace] = values
        print('logout_route:', namespace, urlpatterns)

    def register_storage_provider(self, provider: StorageProvider):
        self.storage_provider = provider

    def logout_storage_provider(self, provider: StorageProvider):
        self.storage_provider = None
        print('logout_storage_provider')

    def register_migration_provider(self, provider: MigrationProvider):
        self.migration_provider = provider

    def logout_migration_provider(self, provider: MigrationProvider):
        self.migration_provider = None
        print('logout_migration_provider')

    def register_app_type(
        self,
        key: str,
        name: str,
        provider: AppTypeProvider,
        serializer: AppBaseSerializer,
    ) -> None:
        if (key, name) not in self.app_types:
            self.app_types.append((key, name))

        if provider is not None and key not in self.app_type_providers:
            self.app_type_providers[key] = provider

        if serializer is not None and key not in self.app_type_serializers:
            self.app_type_serializers[key] = serializer

    def logout_app_type(
        self,
        key: str,
        name: str,
        provider: AppTypeProvider,
        serializer: AppBaseSerializer,
    ) -> None:
        if (key, name) in self.app_types:
            self.app_types.remove((key, name))

        if provider is not None and key in self.app_type_providers:
            self.app_type_providers.pop(key)

        if serializer is not None and key in self.app_type_serializers:
            self.app_type_serializers.pop(key)
        print('logout_app_type:', key)

    def register_auth_rule_type(
        self,
        key: str,
        name: str,
        provider: BaseAuthRuleProvider,
        serializer: AuthRuleBaseSerializer,
    ) -> None:
        if (key, name) not in self.auth_rule_types:
            self.auth_rule_types.append((key, name))

        if provider is not None and key not in self.auth_rule_type_providers:
            self.auth_rule_type_providers[key] = provider
        
        if serializer is not None and key not in self.auth_rule_type_serializers:
            self.auth_rule_type_serializers[key] = serializer

    def logout_auth_rule_type(
        self,
        key: str,
        name: str,
        provider: BaseAuthRuleProvider,
        serializer: AuthRuleBaseSerializer,
    ) -> None:
        if (key, name) in self.auth_rule_types:
            self.auth_rule_types.remove((key, name))

        if provider is not None and key in self.auth_rule_type_providers:
            self.auth_rule_type_providers.pop(key)

        if serializer is not None and key in self.auth_rule_type_serializers:
            self.auth_rule_type_serializers.pop(key)
        print('logout_auth_rule_type:', key)

    def register_sms_provider(self, sms_provider: SMSProvider):
        self.sms_provider = sms_provider

    def logout_sms_provider(self, sms_provider: SMSProvider):
        if self.sms_provider and sms_provider.signature == self.sms_provider.signature:
            self.sms_provider = None
            print('logout_sms_provider:', sms_provider.signature)

    def register_cache_provider(self, cache_provider: CacheProvider):
        self.cache_provider = cache_provider

    def logout_cache_provider(self, cache_provider: CacheProvider):
        self.cache_provider = None
        print('logout_cache_provider')

    def register_tenantuserconfig_provider(self, tenantuserconfig_provider: TenantUserConfigProvider):
        self.tenantuserconfig_provider = tenantuserconfig_provider

    def logout_tenantuserconfig_provider(self, tenantuserconfig_provider: TenantUserConfigProvider):
        self.tenantuserconfig_provider = None
        print('logout_tenantuserconfig_provider')

    def register_authcode_provider(self, authcode_provider: AuthCodeProvider):
        self.authcode_provider = authcode_provider

    def logout_authcode_provider(self, authcode_provider: AuthCodeProvider):
        # if self.authcode_provider and authcode_provider == self.authcode_provider:
        #     self.authcode_provider = None
        self.authcode_provider = None
        print('logout_authcode_provider')

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
