from typing import Optional, List, Dict, TypeVar, Generic
from collections import OrderedDict
from common.provider import (
    ApplicationManageProvider,
    BaseAuthRuleProvider,
    SMSProvider,
    CacheProvider,
    ExternalIdpProvider,
    MFAProvider,
    AuthorizationServerProvider,
    AppTypeProvider,
    StorageProvider,
    MigrationProvider,
    AuthCodeBaseProvider,
    TenantUserConfigProvider,
    LoginRegisterConfigProvider,
    PrivacyNoticeProvider,
    ChildAccountConfigProvider,
    OtherAuthFactorProvider,
    ChildManagerConfigProvider,
    StatisticsProvider,
    DataSyncProvider,
    BackendLoginProvider,
)
from common.serializer import (
    AppBaseSerializer,
    AuthRuleBaseSerializer,
    ExternalIdpBaseSerializer,
    LoginRegisterConfigBaseSerializer,
    OtherAuthFactorBaseSerializer,
    DataSyncBaseSerializer,
    BackendLoginBaseSerializer,
)
from authorization_server.models import AuthorizationServer
from mfa.models import MFA
from common.exception import DuplicatedIdException


class Runtime:

    _instance = None

    sms_provider: SMSProvider = None
    cache_provider: CacheProvider = None
    storage_provider: StorageProvider = None
    authcode_provider: AuthCodeBaseProvider = None
    tenantuserconfig_provider: TenantUserConfigProvider = None
    childaccountconfig_provider: ChildAccountConfigProvider = None
    childmanagerconfig_provider: ChildManagerConfigProvider = None
    migration_provider: MigrationProvider = None
    privacy_notice_provider: PrivacyNoticeProvider = None
    statistics_provider: StatisticsProvider = None

    external_idps: List
    external_idp_providers: Dict[str, ExternalIdpProvider]
    external_idp_serializers: Dict[str, ExternalIdpBaseSerializer]

    authorization_agents: List
    authorization_agent_providers: Dict[str, ExternalIdpProvider]
    authorization_agent_serializers: Dict[str, ExternalIdpBaseSerializer]

    login_register_configs: List
    login_register_config_providers: Dict[str, LoginRegisterConfigProvider]
    login_register_config_serializers: Dict[str, LoginRegisterConfigBaseSerializer]

    other_auth_factors: List
    other_auth_factor_providers: Dict[str, OtherAuthFactorProvider]
    other_auth_factor_serializers: Dict[str, OtherAuthFactorBaseSerializer]

    authorization_servers: List[AuthorizationServer] = []

    mfa_providers: Optional[List] = None

    app_types: List
    app_type_providers: Dict[str, AppTypeProvider]
    app_type_serializers: Dict[str, AppBaseSerializer]

    auth_rule_types: List
    auth_rule_type_providers: Dict[str, BaseAuthRuleProvider]
    auth_rule_type_serializers: Dict[str, AuthRuleBaseSerializer]
    auth_rules = []

    data_sync_extensions: List
    data_sync_providers: Dict[str, DataSyncProvider]
    data_sync_serializers: Dict[str, DataSyncBaseSerializer]

    backend_login_extensions: List
    backend_login_providers: Dict[str, BackendLoginProvider]
    backend_login_serializers: Dict[str, BackendLoginBaseSerializer]
    
    # 应用管理插件列表，控制页面上应用显示等
    application_manage_extensions: List
    application_manage_providers: Dict[str, ApplicationManageProvider]    

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

            cls._instance.authorization_agents = []
            cls._instance.authorization_agent_providers = {}
            cls._instance.authorization_agent_serializers = {}

            cls._instance.login_register_configs = []
            cls._instance.login_register_config_providers = {}
            cls._instance.login_register_config_serializers = {}

            cls._instance.auth_rule_types = []
            cls._instance.auth_rule_type_providers = {}
            cls._instance.auth_rule_type_serializers = {}
            cls._instance.auth_rules = []

            cls._instance.other_auth_factors = []
            cls._instance.other_auth_factor_providers = {}
            cls._instance.other_auth_factor_serializers = {}

            cls._instance.data_sync_extensions = []
            cls._instance.data_sync_providers = {}
            cls._instance.data_sync_serializers = {}

            cls._instance.backend_login_extensions = []
            cls._instance.backend_login_providers = {}
            cls._instance.backend_login_serializers = {}
            
            cls._instance.application_manage_extensions = []
            cls._instance.application_manage_providers = {}

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
        self.authorization_agents = []
        self.authorization_agent_providers = {}
        self.authorization_agent_serializers = {}
        self.login_register_configs = []
        self.login_register_config_providers = {}
        self.login_register_config_serializers = {}
        self.authorization_servers = []
        self.sms_provider = None
        self.cache_provider = None
        self.storage_provider = None
        self.authcode_provider = None
        self.migration_provider = None
        self.privacy_notice_provider = None
        self.statistics_provider = None
        self.other_auth_factors = []
        self.other_auth_factor_providers = {}
        self.other_auth_factor_serializers = {}

        self.auth_rule_types = []
        self.auth_rule_type_providers = {}
        self.auth_rule_type_serializers = {}
        self.auth_rules = []

        self.data_sync_extensions = []
        self.data_sync_providers = {}
        self.data_sync_serializers = {}

        self.backend_login_extensions = []
        self.backend_login_providers = {}
        self.backend_login_serializers = {}
        
        self.application_manage_extensions = []
        self.application_manage_providers = {}

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

    def register_authorization_agent(
        self,
        key: str,
        name: str,
        description: str,
        provider: ExternalIdpProvider,
        serializer: ExternalIdpBaseSerializer = None,
    ):
        if (key, name, description) not in self.authorization_agents:
            self.authorization_agents.append((key, name, description))
        if provider is not None:
            self.authorization_agent_providers[key] = provider

        if serializer is not None:
            self.authorization_agent_serializers[key] = serializer

    def logout_authorization_agent(
        self,
        key: str,
        name: str,
        description: str,
        provider: ExternalIdpProvider,
        serializer: ExternalIdpBaseSerializer = None,
    ):
        if (key, name, description) in self.authorization_agents:
            self.authorization_agents.remove((key, name, description))
        if provider is not None and key in self.authorization_agent_providers:
            self.authorization_agent_providers.pop(key)
        if serializer is not None and key in self.authorization_agent_serializers:
            self.authorization_agent_serializers.pop(key)
        print('logout_authorization_agent:', name)

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

    def register_other_auth_factor(
        self,
        key: str,
        name: str,
        description: str,
        provider: OtherAuthFactorProvider,
        serializer: OtherAuthFactorBaseSerializer = None,
    ):
        if (key, name, description) not in self.other_auth_factors:
            self.other_auth_factors.append((key, name, description))
        if provider is not None:
            self.other_auth_factor_providers[key] = provider

        if serializer is not None:
            self.other_auth_factor_serializers[key] = serializer

    def logout_other_auth_factor(
        self,
        key: str,
        name: str,
        description: str,
        provider: LoginRegisterConfigProvider,
        serializer: LoginRegisterConfigBaseSerializer = None,
    ):
        if (key, name, description) in self.other_auth_factors:
            self.other_auth_factors.remove((key, name, description))
        if provider is not None and key in self.other_auth_factor_providers:
            self.other_auth_factor_providers.pop(key)
        if serializer is not None and key in self.other_auth_factor_serializers:
            self.other_auth_factor_serializers.pop(key)

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

            # 查找已经配置认证规则的应用写入运行时
            from auth_rules.models import TenantAuthRule

            rules = TenantAuthRule.active_objects.filter(type=key, is_apply=True).all()
            if len(rules):
                self.auth_rules.extend(rules)

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

    def register_tenantuserconfig_provider(
        self, tenantuserconfig_provider: TenantUserConfigProvider
    ):
        self.tenantuserconfig_provider = tenantuserconfig_provider

    def logout_tenantuserconfig_provider(
        self, tenantuserconfig_provider: TenantUserConfigProvider
    ):
        self.tenantuserconfig_provider = None
        print('logout_tenantuserconfig_provider')

    def register_childaccountconfig_provider(
        self, childaccountconfig_provider: ChildAccountConfigProvider
    ):
        self.childaccountconfig_provider = childaccountconfig_provider

    def logout_childaccountconfig_provider(
        self, childaccountconfig_provider: ChildAccountConfigProvider
    ):
        self.childaccountconfig_provider = None
        print('logout_childaccountconfig_provider')

    def register_childmanagerconfig_provider(
        self, childmanagerconfig_provider: ChildManagerConfigProvider
    ):
        self.childmanagerconfig_provider = childmanagerconfig_provider

    def logout_childmanagerconfig_provider(
        self, childmanagerconfig_provider: ChildManagerConfigProvider
    ):
        self.childmanagerconfig_provider = None
        print('logout_childmanagerconfig_provider')

    def register_authcode_provider(self, authcode_provider: AuthCodeBaseProvider):
        self.authcode_provider = authcode_provider

    def logout_authcode_provider(self, authcode_provider: AuthCodeBaseProvider):
        # if self.authcode_provider and authcode_provider == self.authcode_provider:
        #     self.authcode_provider = None
        self.authcode_provider = None
        print('logout_authcode_provider')

    def register_privacy_notice_provider(
        self,
        privacy_notice_provider: PrivacyNoticeProvider,
    ):
        self.privacy_notice_provider = privacy_notice_provider

    def logout_privacy_notice_provider(
        self, privacy_notice_provider: PrivacyNoticeProvider
    ):
        self.privacy_notice_provider = None
        print('logout_authcode_provider')

    def register_statistics_provider(self, statistics_provider: StatisticsProvider):
        self.statistics_provider = statistics_provider

    def logout_statistics_provider(self, statistics_provider: StatisticsProvider):
        self.statistics_provider = None
        print('logout_statistics_provider')

    def register_data_sync_extension(
        self,
        key: str,
        name: str,
        description: str,
        provider: DataSyncProvider,
        serializer: DataSyncBaseSerializer = None,
    ):
        if (key, name, description) not in self.data_sync_extensions:
            self.data_sync_extensions.append((key, name, description))
        if provider is not None:
            self.data_sync_providers[key] = provider

        if serializer is not None:
            self.data_sync_serializers[key] = serializer

    def logout_data_sync_extension(
        self,
        key: str,
        name: str,
        description: str,
        provider: DataSyncProvider,
        serializer: DataSyncBaseSerializer = None,
    ):
        if (key, name, description) in self.data_sync_extensions:
            self.data_sync_extensions.remove((key, name, description))
        if provider is not None and key in self.data_sync_providers:
            self.data_sync_providers.pop(key)
        if serializer is not None and key in self.data_sync_serializers:
            self.data_sync_serializers.pop(key)
        print('logout_data_sync_extension:', name)

    def register_backend_login_extension(
        self,
        key: str,
        name: str,
        description: str,
        provider: BackendLoginProvider,
        serializer: BackendLoginBaseSerializer = None,
    ):
        if (key, name, description) not in self.backend_login_extensions:
            self.backend_login_extensions.append((key, name, description))
        if provider is not None:
            self.backend_login_providers[key] = provider
        if serializer is not None:
            self.backend_login_serializers[key] = serializer

    def logout_backend_login_extension(
        self,
        key: str,
        name: str,
        description: str,
        provider: BackendLoginProvider,
        serializer: BackendLoginBaseSerializer = None,
    ):
        if (key, name, description) in self.backend_login_extensions:
            self.backend_login_extensions.remove((key, name, description))
        if provider is not None and key in self.backend_login_providers:
            self.backend_login_providers.pop(key)
        if serializer is not None and key in self.backend_login_serializers:
            self.backend_login_serializers.pop(key)
            
    def register_application_manage_extension(
        self,
        key: str,
        name: str,
        description: str,
        provider: ApplicationManageProvider,
    ):
        if (key, name, description) not in self.application_manage_extensions:
            self.application_manage_extensions.append((key, name, description))
        if provider is not None:
            self.application_manage_providers[key] = provider
            
    def logout_application_manage_extension(
        self,
        key: str,
        name: str,
        description: str,
        provider: ApplicationManageProvider,
    ):
        if (key, name, description) in self.application_manage_extensions:
            self.application_manage_extensions.remove((key, name, description))
        if provider is not None and key in self.application_manage_providers:
            self.application_manage_providers.pop(key)

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
