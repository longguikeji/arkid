from common.provider import DataSyncProvider
from .ad_group_provider import AdGroupProvider
from .ad_user_provider import AdUserProvider
from scim_server.service.provider_base import ProviderBase
from scim_server.schemas.core2_enterprise_user import Core2EnterpriseUser
from scim_server.schemas.core2_group import Core2Group
from scim_server.schemas.schema_identifiers import SchemaIdentifiers
from scim_server.exceptions import (
    ArgumentNullException,
    ArgumentException,
    NotFoundException,
)
from data_sync.models import DataSyncConfig
from ldap3 import Server, Connection
from .utils import load_config
from django.urls import reverse
from config import get_app_config


class AdDataSyncProvider(DataSyncProvider, ProviderBase):
    def __init__(self, tenant_uuid) -> None:
        super().__init__()
        config = load_config(tenant_uuid)
        if not config:
            raise NotFoundException('Ad server config not found')
        self.group_provider = AdGroupProvider(config)
        self.user_provider = AdUserProvider(config)

    @classmethod
    def create(cls, tenant_uuid, data):
        host = data.get("host")
        port = data.get("port")
        bind_dn = data.get("bind_dn")
        bind_password = data.get("bind_password")
        root_dn = data.get("root_dn")
        use_tls = data.get("use_tls")
        server_host = get_app_config().get_host()
        user_url = server_host + reverse('api:ad_data_sync:ad-users', args=[tenant_uuid])
        group_url = server_host + reverse('api:ad_data_sync:ad-groups', args=[tenant_uuid])

        return {
            "host": host,
            "port": port,
            "bind_dn": bind_dn,
            "bind_password": bind_password,
            "root_dn": root_dn,
            "use_tls": use_tls,
            "user_url": user_url,
            "group_url": group_url,
        }

    @classmethod
    def update(cls, tenant_uuid, data):
        host = data.get("host")
        port = data.get("port")
        bind_dn = data.get("bind_dn")
        bind_password = data.get("bind_password")
        root_dn = data.get("root_dn")
        use_tls = data.get("use_tls")
        server_host = get_app_config().get_host()
        user_url = server_host + reverse('api:ad_data_sync:ad-users', args=[tenant_uuid])
        group_url = server_host + reverse('api:ad_data_sync:ad-groups', args=[tenant_uuid])

        return {
            "host": host,
            "port": port,
            "bind_dn": bind_dn,
            "bind_password": bind_password,
            "root_dn": root_dn,
            "use_tls": use_tls,
            "user_url": user_url,
            "group_url": group_url,
        }

    def create_async2(self, resource, correlation_identifier):
        if isinstance(resource, Core2EnterpriseUser):
            return self.user_provider.create_async2(resource, correlation_identifier)

        if isinstance(resource, Core2Group):
            return self.group_provider.create_async2(resource, correlation_identifier)

        raise NotImplementedError()

    def delete_async2(self, resource_identifier, correlation_identifier):
        if (
            resource_identifier.schema_identifier
            == SchemaIdentifiers.Core2EnterpriseUser
        ):
            return self.user_provider.delete_async2(
                resource_identifier, correlation_identifier
            )

        if resource_identifier.schema_identifier == SchemaIdentifiers.Core2Group:
            return self.group_provider.delete_async2(
                resource_identifier, correlation_identifier
            )

        raise NotImplementedError()

    def query_async2(self, parameters, correlation_identifier):
        if parameters.schema_identifier == SchemaIdentifiers.Core2EnterpriseUser:
            return self.user_provider.query_async2(parameters, correlation_identifier)

        if parameters.schema_identifier == SchemaIdentifiers.Core2Group:
            return self.group_provider.query_async2(parameters, correlation_identifier)

        raise NotImplementedError()

    def replace_async2(self, resource, correlation_identifier):
        if isinstance(resource, Core2EnterpriseUser):
            return self.user_provider.replace_async2(resource, correlation_identifier)

        if isinstance(resource, Core2Group):
            return self.group_provider.replace_async2(resource, correlation_identifier)

    def retrieve_async2(self, parameters, correlation_identifier):
        if parameters.schema_identifier == SchemaIdentifiers.Core2EnterpriseUser:
            return self.user_provider.retrieve_async2(
                parameters, correlation_identifier
            )

        if parameters.schema_identifier == SchemaIdentifiers.Core2Group:
            return self.group_provider.retrieve_async2(
                parameters, correlation_identifier
            )

        raise NotImplementedError()

    def update_async2(self, patch, correlation_identifier):
        if not patch:
            raise ArgumentNullException('patch')
        if not patch.resource_identifier.identifier:
            raise ArgumentException('patch')
        if not patch.resource_identifier.schema_identifier:
            raise ArgumentException('patch')

        if (
            patch.resource_identifier.schema_identifier
            == SchemaIdentifiers.Core2EnterpriseUser
        ):
            return self.user_provider.update_async2(patch, correlation_identifier)

        if patch.resource_identifier.schema_identifier == SchemaIdentifiers.Core2Group:
            return self.group_provider.update_async2(patch, correlation_identifier)

        raise NotImplementedError()


class AdDataSyncClientProvider(DataSyncProvider):
    @classmethod
    def create(cls, tenant_uuid, data):
        data['tenant_uuid'] = tenant_uuid.hex
        data['task'] = 'extension_root.ad_data_sync.tasks.sync'
        scim_server_uuid = data['scim_server_uuid']
        scim_server = DataSyncConfig.objects.filter(uuid=scim_server_uuid).first()
        data['scim_server_name'] = scim_server.name
        data['user_url'] = scim_server.data['user_url']
        data['group_url'] = scim_server.data['group_url']
        return data

    @classmethod
    def update(cls, tenant_uuid, data):
        data['tenant_uuid'] = tenant_uuid.hex
        data['task'] = 'extension_root.ad_data_sync.tasks.sync'
        scim_server_uuid = data['scim_server_uuid']
        scim_server = DataSyncConfig.objects.filter(uuid=scim_server_uuid).first()
        data['scim_server_name'] = scim_server.name
        data['user_url'] = scim_server.data['user_url']
        data['group_url'] = scim_server.data['group_url']
        return data
