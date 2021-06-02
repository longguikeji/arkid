from typing import Any, Dict, Optional
from abc import abstractmethod
import uuid
from django.core.files import File


class SMSProvider:
    @abstractmethod
    def send_auth_code(self, mobile, code):
        pass


class EmailProvider:
    @abstractmethod
    def send_auth_code(self, mobile, code):
        raise NotImplementedError


class AuthCodeProvider:
    @abstractmethod
    def get_authcode_picture(self):
        pass

    def generate_key(self):
        key = '{}.jpg'.format(
            uuid.uuid4().hex
        )
        return key


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
