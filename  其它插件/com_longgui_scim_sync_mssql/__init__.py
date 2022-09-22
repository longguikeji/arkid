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
import json
from .utils import get_connection, get_scim_group, get_scim_user
from .mssql_sync_client import MssqlSyncClient
from ninja import Schema
from typing import List
from collections import defaultdict


class MssqlServerAttrMapItem(Schema):
    source_attr: str = Field(title=_('SQL Server Source Attribute', 'SQL Server属性'))
    target_attr: str = Field(title=_('SCIM Target Attribute', 'SCIM属性'))


class MssqlClientAttrMapItem(Schema):
    source_attr: str = Field(title=_('SCIM Source Attribute', 'SCIM属性'))
    target_attr: str = Field(title=_('SQL Server Target Attribute', 'SQL Server属性'))


MssqlClientConfig = create_extension_schema(
    "MssqlClientConfig",
    __file__,
    fields=[
        ('server', str, Field(title=_("Sql Server Host", "Sql Server数据库地址"))),
        (
            'port',
            int,
            Field(default=1433, title=_("Sql Server Port", "Sql Server数据库端口号")),
        ),
        ('user', str, Field(title=_("Sql Server User", "Sql Server数据库用户"))),
        ('password', str, Field(title=_("Sql Server Password", "Sql Server数据库用户密码"))),
        ('database', str, Field(title=_("Sql Server Database", "Sql Server数据库名"))),
        ('target_user_table', str, Field(title=_("Target User Table", "用户数据表"))),
        ('target_group_table', str, Field(title=_("Target Group Table", "组织数据表"))),
        (
            'group_table_parent_fk',
            str,
            Field(title=_("Group Table Parent Foreign Key Field", "组织表Parent外键字段")),
        ),
        (
            'user_table_group_fk',
            str,
            Field(title=_("User Table Group Foreign Key Field", "用户表Group外键字段")),
        ),
        (
            'user_group_rel_table',
            str,
            Field(title=_("User Group Relation Table", "用户和组织多对多关系表")),
        ),
        (
            'user_group_rel_user_fk',
            str,
            Field(title=_("User Foreign Field", "用户组织关系表User外键字段")),
        ),
        (
            'user_group_rel_group_fk',
            str,
            Field(title=_("Group Foreign Field", "用户组织关系表Group外键字段")),
        ),
        (
            'user_attr_map',
            List[MssqlClientAttrMapItem],
            Field(default=[], title=_("User Attr Map", "用户属性映射"), format="dynamic"),
        ),
        (
            'group_attr_map',
            List[MssqlClientAttrMapItem],
            Field(default=[], title=_("Group Attr Map", "组织属性映射"), format="dynamic"),
        ),
    ],
    base_schema=BaseScimSyncClientSchema,
)

MssqlServerConfig = create_extension_schema(
    "MssqlServerConfig",
    __file__,
    fields=[
        ('server', str, Field(title=_("Sql Server Host", "Sql Server数据库地址"))),
        (
            'port',
            int,
            Field(default=1433, title=_("Sql Server Port", "Sql Server数据库端口号")),
        ),
        ('user', str, Field(title=_("Sql Server User", "Sql Server数据库用户"))),
        ('password', str, Field(title=_("Sql Server Password", "Sql Server数据库用户密码"))),
        ('database', str, Field(title=_("Sql Server Database", "Sql Server数据库名"))),
        ('users_sql', str, Field(title=_("Sql Server User Sql", "查询用户列表SQL"))),
        ('groups_sql', str, Field(title=_("Sql Server Group Sql", "查询组织列表SQL"))),
        (
            'group_table_parent_fk',
            str,
            Field(title=_("Group Table Parent Foreign Key Field", "组织表Parent外键字段")),
        ),
        (
            'user_table_group_fk',
            str,
            Field(title=_("User Table Group Foreign Key Field", "用户表Group外键字段")),
        ),
        (
            'user_group_rel_table',
            str,
            Field(title=_("User Group Relation Table", "用户和组织多对多关系表")),
        ),
        (
            'user_group_rel_user_fk',
            str,
            Field(title=_("User Foreign Field", "用户组织关系表User外键字段")),
        ),
        (
            'user_group_rel_group_fk',
            str,
            Field(title=_("Group Foreign Field", "用户组织关系表Group外键字段")),
        ),
        (
            'user_attr_map',
            List[MssqlServerAttrMapItem],
            Field(default=[], title=_("User Attr Map", "用户属性映射"), format="dynamic"),
        ),
        (
            'group_attr_map',
            List[MssqlServerAttrMapItem],
            Field(title=_("Group Attr Map", "组织属性映射"), format="dynamic"),
        ),
    ],
    base_schema=BaseScimSyncServerSchema,
)


class ScimSyncMssqlExtension(ScimSyncExtension):
    def load(self):
        self.register_scim_sync_schema('Mssql', MssqlClientConfig, MssqlServerConfig)
        super().load()

    ############################################################################
    # AD Client: 同步User, Group数据
    ############################################################################
    def sync(self, config):
        """
        Args:
            config (arkid.extension.models.TenantExtensionConfig): Client模式创建的配置
        """
        logger.info(
            f"============= Sync Start With Config: {config}/{config.config} ================"
        )
        groups, users = self.get_groups_users(config)
        client = MssqlSyncClient(config.config, groups, users)
        client.sync()
        # if not groups or not users:
        #     return
        # self.sync_groups(groups, config)
        # self.sync_users(users, config)

    def sync_groups(self, groups, config):
        """
        Args:
            groups (List): SCIM Server返回的组织列表
            config (arkid.extension.models.TenantExtensionConfig): Client模式创建的配置
        """
        pass

    def sync_users(self, users, config):
        """
        Args:
            users (List): SCIM Server返回的用户列表
            config (arkid.extension.models.TenantExtensionConfig): Client模式创建的配置
        """
        pass

    ############################################################################
    # AD Server: 获取Group数据
    ############################################################################

    def _get_all_scim_groups(self, config):
        result = []
        rows = []
        group_members = defaultdict(list)
        group_attr_map = config.get("group_attr_map", [])
        match_attr = "id"

        for item in group_attr_map:
            if item.get("target_attr") == "id":
                match_attr = item.get("source_attr")
                break

        conn = get_connection(config)
        cursor = conn.cursor(as_dict=True)
        cursor.execute(config.get("groups_sql"))
        row = cursor.fetchone()
        while row:
            rows.append(row)
            parent_fk = config.get("group_table_parent_fk")
            if parent_fk:
                group_id = row.get(match_attr)
                parent_id = row.get(parent_fk)
                if parent_id:
                    group_members[parent_id].append(group_id)
            row = cursor.fetchone()

        for group in rows:
            group_id = group.get(match_attr)
            members = group_members.get(group_id, [])
            scim_group = get_scim_group(group, members, group_attr_map)
            result.append(scim_group)
        conn.close()
        return result

    ############################################################################
    # AD Server: 获取User数据
    ############################################################################

    def _get_all_scim_users(self, config):
        result = []
        user_attr_map = config.get("user_attr_map", [])
        match_attr = "id"

        for item in user_attr_map:
            if item.get("target_attr") == "id":
                match_attr = item.get("source_attr")
                break

        conn = get_connection(config)
        cursor = conn.cursor(as_dict=True)
        cursor.execute(config.get("users_sql"))
        row = cursor.fetchone()
        while row:
            user_table_group_fk = config.get("user_table_group_fk")
            user_group_rel_table = config.get("user_group_rel_table")
            user_group_rel_user_fk = config.get("user_group_rel_user_fk")
            user_group_rel_group_fk = config.get("user_group_rel_group_fk")

            if user_table_group_fk:
                groups = [row.get(user_table_group_fk)]
            elif user_group_rel_table:
                if user_group_rel_user_fk and user_group_rel_group_fk:

                    conn1 = get_connection(config)
                    cursor1 = conn1.cursor(as_dict=True)
                    user_id = row.get(match_attr)
                    cursor1.execute(
                        f"select {user_group_rel_group_fk} from {user_group_rel_table} where {user_group_rel_user_fk} = {user_id}"
                    )
                    groups = cursor1.fetchall()
                    groups = [grp[user_group_rel_group_fk] for grp in groups]
                    conn1.close()
            else:
                groups = []

            scim_user = get_scim_user(row, groups, user_attr_map)
            result.append(scim_user)
            row = cursor.fetchone()
        conn.close()
        return result

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
        self.connection = get_connection(config.config)
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
        self.connection = get_connection(config.config)
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


extension = ScimSyncMssqlExtension()
