from typing import Any, Dict, Optional
from abc import abstractmethod, ABC
import uuid
from django.core.files import File


class SMSProvider:
    @abstractmethod
    def send_auth_code(self, mobile, code, template):
        pass


class EmailProvider:
    @abstractmethod
    def send_auth_code(self, mobile, code):
        raise NotImplementedError


class AuthCodeBaseProvider:
    def generate_key(self):
        key = '{}.png'.format(uuid.uuid4().hex)
        return key

    @abstractmethod
    def get_authcode_picture(self):
        pass


class StorageProvider:
    @abstractmethod
    def upload(self, file: File) -> str:
        raise NotImplementedError

    @abstractmethod
    def resolve(self, key: str) -> str:
        raise NotImplementedError

    def generate_key(self, file: File):
        key = '{}.{}'.format(
            uuid.uuid4().hex,
            file.name.split('.')[-1],
        )
        return key


class CacheProvider:
    @abstractmethod
    def set(self, key: str, value: any):
        pass

    @abstractmethod
    def get(self, key: str) -> any:
        pass


class ExternalIdpProvider:

    name: Optional[str]
    bind_key: str

    def __init__(self) -> None:
        self.name = None

    @abstractmethod
    def create(self, tenant_uuid, external_idp) -> Dict:
        raise NotImplementedError()

    @abstractmethod
    def get_groups(self):
        """
        ExternalIDP => ArkID
        """
        pass

    @abstractmethod
    def get_users(self):
        """
        ExternalIDP => ArkID
        """
        pass


class ChildAccountConfigProvider:
    pass


class ChildManagerConfigProvider:
    pass


class TenantUserConfigProvider:
    pass


class AuthorizationAgentProvider:

    name: Optional[str]
    bind_key: str

    def __init__(self) -> None:
        self.name = None

    @abstractmethod
    def create(self, tenant_uuid, external_idp) -> Dict:
        raise NotImplementedError()

    @abstractmethod
    def authenticate(self):
        """
        ExternalIDP => ArkID
        """
        pass


class DataSyncProvider:
    @classmethod
    def create(cls, tenant_uuid, config_data):
        pass

    @classmethod
    def update(cls, tenant_uuid, config_data):
        pass


class AuthorizationServerProvider:

    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None

    def __init__(self, id: str, name: str, description: str = '') -> None:
        self.id = id
        self.name = name
        self.description = description

    @property
    def app_settings_schema(self):
        """
        描述创建App时候需要配置的参数
        """
        return []


class MFAProvider:
    @abstractmethod
    def setup(self):
        pass

    @abstractmethod
    def teardown(self):
        pass

    @abstractmethod
    def verify(self):
        pass


class AppTypeProvider:
    @abstractmethod
    def create(self, app) -> Dict:
        raise NotImplementedError()

    @abstractmethod
    def update(self):
        raise NotImplementedError()

    @abstractmethod
    def delete(self):
        raise NotImplementedError()


class MigrationProvider:
    @abstractmethod
    def migrate(self, tenant_uuid):
        raise NotImplementedError


class LoginRegisterConfigProvider:
    @property
    def login_form(self):
        return None

    @property
    def register_form(self):
        return None

    @property
    def reset_password_form(self):
        return None

    def authenticate(self, request):
        '''login'''
        pass

    def register_user(self, request):
        '''register'''
        pass

    def reset_password(self, request):
        pass


class PrivacyNoticeProvider:
    @classmethod
    def load_privacy(cls, request):
        raise NotImplementedError


class BaseAuthRuleProvider:
    @abstractmethod
    def create(self, auth_rule, data) -> Dict:
        raise NotImplementedError()

    @abstractmethod
    def update(self):
        raise NotImplementedError()

    @abstractmethod
    def delete(self):
        raise NotImplementedError()

    @abstractmethod
    def run(self, *args, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def change_form(self, auth_rule, request, form, tenant):
        raise NotImplementedError()

    @abstractmethod
    def authenticate_failed(self, auth_rule, request, form, tenant, extension):
        return form

    @abstractmethod
    def authenticate_success(self, auth_rule, request, form, user, tenant, extension):
        print(form)
        return form


class OtherAuthFactorProvider:
    def authenticate(self, request):
        '''login'''
        pass


class StatisticsProvider:
    @abstractmethod
    def get_charts(self, tenant) -> any:
        pass
