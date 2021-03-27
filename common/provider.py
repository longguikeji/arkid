from typing import (
    Dict, Optional
)
from abc import abstractmethod

class SMSProvider:

    @abstractmethod
    def send_auth_code(self, mobile, code):
        pass


class EmailProvider:

    @abstractmethod
    def send_auth_code(self, mobile, code):
        pass


class StorageProvider:

    @abstractmethod
    def upload(self, path: str):
        pass

    @abstractmethod
    def download(self, path: str):
        pass

    @abstractmethod
    def remove(self, path: str):
        pass

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
    def create(self, external_idp) -> Dict:
        raise NotImplementedError()

    @abstractmethod
    def get_groups(self):
        '''
        ExternalIDP => ArkID
        '''
        pass

    @abstractmethod
    def get_users(self):
        '''
        ExternalIDP => ArkID
        '''
        pass


class AuthorizationServerProvider:

    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None

    def __init__(self, id: str, name: str, description: str='') -> None:
        self.id = id
        self.name = name 
        self.description = description

    @property
    def app_settings_schema(self):
        '''
        描述创建App时候需要配置的参数
        '''
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


class AuthorizationServerProvider:

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
