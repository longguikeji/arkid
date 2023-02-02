from email.headerregistry import Group
from email.mime import base
from ninja import Field
from typing import Optional
from types import SimpleNamespace
from arkid.core import event
from arkid.core.extension import Extension, create_extension_schema
from arkid.core.event import SEND_SMS
from arkid.core.translation import gettext_default as _
from arkid.core.extension.scim_sync import (
    BaseScimSyncClientSchema,
    BaseScimSyncServerSchema,
    ScimSyncExtension,
)
from arkid.common.logger import logger
from arkid.core.models import UserGroup, User, Tenant
from scim_server.schemas.core2_enterprise_user import Core2EnterpriseUser
from scim_server.schemas.core2_group import Core2Group
from scim_server.protocol.path import Path
from scim_server.utils import (
    compose_core2_user,
    compose_enterprise_extension,
    compose_core2_group,
    compose_core2_group_member,
)
from scim_server.schemas.schema_identifiers import SchemaIdentifiers
from scim_server.schemas.member import Member
from scim_server.schemas.user_groups import UserGroup as ScimUserGroup
from django.db.utils import IntegrityError
from scim_server.exceptions import NotImplementedException
import ldap3
import json
from .utils import get_ad_connection, get_scim_group, get_scim_user
from .ad_sync_client import ADSyncClient
from ninja import Schema
from typing import List
from enum import Enum


class LdapServerType(str, Enum):
    AD = _('AD', 'AD')
    openldap = _('openldap', 'openldap')


class ADAttrMapItem(Schema):
    source_attr: str = Field(title=_('SCIM Source Attribute', 'SCIM属性'))
    target_attr: str = Field(title=_('AD Target Attribute', 'AD属性'))
    is_match_attr: bool = Field(title=_('Is Match Attribute', '是否用于匹配'))


ADClientConfig = create_extension_schema(
    "ADClientConfig",
    __file__,
    fields=[
        ('host', str, Field(title=_("AD Server Host", "AD服务器地址"))),
        ('port', int, Field(title=_("AD Server Port", "AD服务器端口号"))),
        ('bind_dn', str, Field(title=_("AD Server bind_dn", "账号DN"))),
        ('bind_password', str, Field(title=_("AD Server bind_password", "账号DN密码"))),
        ('root_dn', str, Field(title=_("AD Server root_dn", "同步目标组织DN"))),
        ('use_tls', bool, Field(title=_("AD Server Use TLS", "是否使用TLS"))),
        (
            'ldap_server_type',
            LdapServerType,
            Field(title=_("LDAP Server Type", "LDAP服务器类型")),
        ),
        (
            'user_attr_map',
            List[ADAttrMapItem],
            Field(default=[], title=_("User Attr Map", "用户属性映射"), format="dynamic"),
        ),
        # ('group_attr_map', str, Field(title=_("Group Attr Map", "组织属性映射"))),
    ],
    base_schema=BaseScimSyncClientSchema,
)

ADServerConfig = create_extension_schema(
    "ADServerConfig",
    __file__,
    fields=[
        ('host', str, Field(title=_("AD Server Host", "AD服务器地址"))),
        ('port', int, Field(title=_("AD Server Port", "AD服务器端口号"))),
        ('bind_dn', str, Field(title=_("AD Server bind_dn", "账号DN"))),
        ('bind_password', str, Field(title=_("AD Server bind_password", "账号DN密码"))),
        ('root_dn', str, Field(title=_("AD Server root_dn", "同步目标组织DN"))),
        ('use_tls', bool, Field(title=_("AD Server Use TLS", "是否使用TLS"))),
        (
            'ldap_server_type',
            LdapServerType,
            Field(title=_("LDAP Server Type", "LDAP服务器类型")),
        ),
    ],
    base_schema=BaseScimSyncServerSchema,
)


class ScimSyncADExtension(ScimSyncExtension):
    def load(self):
        self.register_scim_sync_schema('LDAP', ADClientConfig, ADServerConfig)
        super().load()

    ############################################################################
    # AD Client: 同步User, Group数据
    ############################################################################
    def sync(self, config, sync_log):
        """
        Args:
            config (arkid.extension.models.TenantExtensionConfig): Client模式创建的配置
        """
        logger.info(
            f"============= Sync Start With Config: {config}/{config.config} ================"
        )
        groups, users = self.get_groups_users(config)
        client = ADSyncClient(config.config, sync_log, groups, users)
        client.sync()
        # if not groups or not users:
        #     return
        # self.sync_groups(groups, config)
        # self.sync_users(users, config)

    def sync_groups(self, groups, config, sync_log):
        """
        Args:
            groups (List): SCIM Server返回的组织列表
            config (arkid.extension.models.TenantExtensionConfig): Client模式创建的配置
        """
        pass

    def sync_users(self, users, config, sync_log):
        """
        Args:
            users (List): SCIM Server返回的用户列表
            config (arkid.extension.models.TenantExtensionConfig): Client模式创建的配置
        """
        pass

    ############################################################################
    # AD Server: 获取Group数据
    ############################################################################
    def convert_ad_ou_to_scim_group(self, ad_group, elements):
        members = [m["attributes"] for m in elements]
        group_attr_map = {"objectGUID": "id", "name": "displayName"}
        return get_scim_group(ad_group["attributes"], members, group_attr_map)

    def convert_openldap_ou_to_scim_group(self, openldap_group, elements):
        members = [m["attributes"] for m in elements]
        group_attr_map = {"entryUUID": "id", "ou": "displayName"}
        return get_scim_group(openldap_group["attributes"], members, group_attr_map)

    def _get_scim_groups_from_ou(self, ou, groups_dict):
        if self.ldap_server_type == 'AD':
            search_filter = "(objectCategory=organizationalUnit)"
            attrs = "*"
        else:
            search_filter = "(objectClass=organizationalUnit)"
            attrs = ["*", "+"]
        elements = self.connection.extend.standard.paged_search(
            search_base=ou["dn"],
            search_filter=search_filter,
            search_scope=ldap3.LEVEL,
            paged_size=50,
            attributes=attrs,
            generator=False,
        )
        if self.ldap_server_type == 'AD':
            groups_dict[ou["dn"]] = self.convert_ad_ou_to_scim_group(ou, elements)
        else:
            groups_dict[ou["dn"]] = self.convert_openldap_ou_to_scim_group(ou, elements)
        for element in elements:
            if element["dn"] != ou["dn"]:
                self._get_scim_groups_from_ou(element, groups_dict)

    def _get_all_scim_groups(self, config):
        self.ldap_server_type = config.get('ldap_server_type')
        groups_dict = {}
        if self.ldap_server_type == 'AD':
            search_filter = "(objectCategory=organizationalUnit)"
            attrs = "*"
        else:
            search_filter = "(objectClass=organizationalUnit)"
            attrs = ["*", "+"]
        root_ou = self.connection.search(
            search_base=config.get('root_dn'),
            search_filter=search_filter,
            search_scope=ldap3.BASE,
            attributes=attrs,
        )
        if root_ou:
            entries = json.loads(self.connection.response_to_json())["entries"]
            root_ou = entries[0]
            self._get_scim_groups_from_ou(root_ou, groups_dict)
            return list(groups_dict.values())
        else:
            return []

    ############################################################################
    # AD Server: 获取User数据
    ############################################################################

    def get_ou_dns(self):
        self.ou_dns = {}
        if self.ldap_server_type == 'AD':
            search_filter = f"(objectCategory=organizationalUnit)"
            attrs = "*"
        elif self.ldap_server_type == 'openldap':
            search_filter = f"(objectClass=organizationalUnit)"
            attrs = ["*", "+"]
        elements = self.connection.extend.standard.paged_search(
            search_base=self.root_dn,
            search_filter=search_filter,
            search_scope=ldap3.SUBTREE,
            paged_size=100,
            attributes=attrs,
        )
        for element in elements:
            self.ou_dns[element["dn"]] = element["attributes"]

    def convert_ad_user_to_scim_user(self, ad_user):
        """
        user attr添加ouId用于识别用户属于哪个组织下
        """
        user_attr_map = {
            "objectGUID": "id",
            "sAMAccountName": "userName",
            "displayName": "name.formatted",
            "sn": "name.familyName",
            "givenName": "name.givenName",
            "employeeID": "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User:employeeNumber",
            "mail": 'emails[type eq "work"].value',
        }
        dn = ad_user["dn"]
        attrs = ad_user["attributes"]
        ou_dn = dn.split(",")[1:]
        ou_dn = ",".join(ou_dn)
        if not hasattr(self, "ou_dns"):
            self.get_ou_dns()
        if ou_dn in self.ou_dns:
            attrs["ouID"] = self.ou_dns[ou_dn]["objectGUID"]
        else:
            logger.warning(f"No OU find with dn{ou_dn}")
        return get_scim_user(attrs, user_attr_map)

    def convert_openldap_user_to_scim_user(self, openldap_user):
        """
        user attr添加ouId用于识别用户属于哪个组织下
        """
        user_attr_map = {
            "entryUUID": "id",
            "cn": "userName",
            "displayName": "name.formatted",
            "sn": "name.familyName",
            "givenName": "name.givenName",
            "employeeNumber": "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User:employeeNumber",
            "mail": 'emails[type eq "work"].value',
        }

        dn = openldap_user["dn"]
        attrs = openldap_user["attributes"]
        ou_dn = dn.split(",")[1:]
        ou_dn = ",".join(ou_dn)
        if not hasattr(self, "ou_dns"):
            self.get_ou_dns()
        if ou_dn in self.ou_dns:
            attrs["ouID"] = self.ou_dns[ou_dn]["entryUUID"]
        else:
            logger.warning(f"No OU find with dn{ou_dn}")
            attrs["ouID"] = self.ou_dns[self.root_dn]["entryUUID"]

        return get_scim_user(attrs, user_attr_map)

    def _get_all_scim_users(self, config):
        self.ldap_server_type = config.get('ldap_server_type')
        search_filter = None
        if self.ldap_server_type == 'AD':
            search_filter = f"(objectClass=user)"
            attrs = "*"
        elif self.ldap_server_type == 'openldap':
            search_filter = f"(objectClass=inetOrgPerson)"
            attrs = ["*", "+"]
        if not search_filter:
            raise Exception("Unsupported ldap server type")
        self.root_dn = config.get('root_dn')
        res = self.connection.extend.standard.paged_search(
            search_base=self.root_dn,
            search_filter=search_filter,
            search_scope=ldap3.SUBTREE,
            paged_size=50,
            attributes=attrs,
        )
        if not res:
            return []
        all_users = []
        for item in res:
            if self.ldap_server_type == 'AD':
                user = self.convert_ad_user_to_scim_user(item)
            else:
                user = self.convert_openldap_user_to_scim_user(item)
            all_users.append(user)
        return all_users

    def query_users(self, request, parameters, correlation_identifier):
        """
        将ArkID中的用户转换成scim_server中的符合SCIM标准的Core2EnterpriseUser对象
        Args:
            request (HttpRequest): Django 请求
            parameters (scim_server.protocol.query_parameters.QueryParameters): Query请求对象
            correlation_identifier (str): 请求唯一标识
        Returns:
            List[Core2EnterpriseUser]: 返回scim_server模块中的标准用户对象列表
        """
        config_id = request.resolver_match.kwargs.get('config_id')
        config = self.get_config_by_id(config_id)
        self.connection = get_ad_connection(config.config)
        if not parameters.alternate_filters:
            all_users = self._get_all_scim_users(config.config)
            return all_users

    def query_groups(self, request, parameters, correlation_identifier):
        """
        将ArkID中的组织转换成scim_server中的符合SCIM标准的Core2Group对象
        Args:
            request (HttpRequest): Django 请求
            parameters (scim_server.protocol.query_parameters.QueryParameters): Query请求对象
            correlation_identifier (str): 请求唯一标识
        Returns:
            List[Core2Group]: 返回scim_server模块中的标准组织对象列表
        """
        config_id = request.resolver_match.kwargs.get('config_id')
        config = self.get_config_by_id(config_id)
        self.connection = get_ad_connection(config.config)
        if not parameters.alternate_filters:
            groups = self._get_all_scim_groups(config.config)
            return groups

    def create_user(self, request, resource, correlation_identifier):
        raise NotImplementedException()

    def create_group(self, request, resource, correlation_identifier):
        raise NotImplementedException()

    def delete_user(self, request, resource_identifier, correlation_identifier):
        raise NotImplementedException()

    def delete_group(self, request, resource_identifier, correlation_identifier):
        raise NotImplementedException()

    def replace_user(self, request, resource, correlation_identifier):
        raise NotImplementedException()

    def replace_group(self, request, resource, correlation_identifier):
        raise NotImplementedException()

    def retrieve_user(self, request, parameters, correlation_identifier):
        raise NotImplementedException()

    def retrieve_group(self, request, parameters, correlation_identifier):
        raise NotImplementedException()

    def update_user(self, request, patch, correlation_identifier):
        raise NotImplementedException()

    def update_group(self, request, patch, correlation_identifier):
        raise NotImplementedException()


extension = ScimSyncADExtension()
