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
from .utils import get_connection, get_scim_group, get_scim_user
from .db_sync_client import DBSyncClient
from ninja import Schema
from typing import List
from collections import defaultdict
from enum import Enum
import MySQLdb


class MssqlServerAttrMapItem(Schema):
    source_attr: str = Field(title=_('Server Mode DB Source Attribute', '数据库字段'))
    target_attr: str = Field(title=_('Server Mode SCIM Target Attribute', 'SCIM属性'))


class MssqlClientAttrMapItem(Schema):
    source_attr: str = Field(title=_('Client Mode SCIM Source Attribute', 'SCIM属性'))
    target_attr: str = Field(title=_('Client Mode Database Target Attribute', '数据库字段'))


class DBType(str, Enum):
    sqlserver = _('sqlserver', 'sqlserver')
    mysql = _('mysql', 'mysql')


DBClientConfig = create_extension_schema(
    "DBClientConfig",
    __file__,
    fields=[
        (
            'db_type',
            DBType,
            Field(title=_("Database Type", "数据库类型"), default="mysql"),
        ),
        ('server', str, Field(title=_("DB Server Host", "数据库地址"))),
        (
            'port',
            int,
            Field(default=3306, title=_("DB Server Port", "数据库端口号")),
        ),
        ('user', str, Field(title=_("DB Server User", "数据库用户"))),
        ('password', str, Field(title=_("DB Server Password", "数据库用户密码"))),
        ('database', str, Field(title=_("DB Server Database", "数据库名"))),
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

DBServerConfig = create_extension_schema(
    "DBServerConfig",
    __file__,
    fields=[
        (
            'db_type',
            DBType,
            Field(title=_("Database Type", "数据库类型"), default="mysql"),
        ),
        ('server', str, Field(title=_("DB Server Host", "数据库地址"))),
        (
            'port',
            int,
            Field(default=3306, title=_("DB Server Port", "数据库端口号")),
        ),
        ('user', str, Field(title=_("DB Server User", "数据库用户"))),
        ('password', str, Field(title=_("DB Server Password", "数据库用户密码"))),
        ('database', str, Field(title=_("DB Server Database", "数据库名"))),
        ('target_user_table', str, Field(title=_("DB Server User Table", "用户数据表"))),
        (
            'target_group_table',
            str,
            Field(title=_("DB Server Group Table", "组织数据表")),
        ),
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
        self.register_scim_sync_schema('Database', DBClientConfig, DBServerConfig)
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
        client = DBSyncClient(config.config, sync_log, groups, users)
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

    def get_cursor(self, config, conn):
        self.db_type = config.get('db_type')
        if self.db_type == 'mysql':
            return conn.cursor(MySQLdb.cursors.DictCursor)
        elif self.db_type == 'sqlserver':
            return conn.cursor(as_dict=True)
        else:
            raise Exception("Unsupported db type")

    ############################################################################
    # AD Server: 获取Group数据
    ############################################################################

    def _get_group_parent_match_id(self, conn, config, group_row, parent_fk):
        target_group_table = config.get("target_group_table")
        parent_row_id = group_row.get(parent_fk.split(":")[0])
        if parent_row_id:
            cursor = self.get_cursor(config, conn)
            sql = f"select * from {target_group_table} where {parent_fk.split(':')[1]} = %s"
            cursor.execute(sql, (parent_row_id,))
            row = cursor.fetchone()
            cursor.close()
            if row:
                parent_match_id = row.get(self.group_match_attr)
                return parent_match_id
            else:
                logger.error(f'No parent record {parent_row_id} found')
                return None
        else:
            return None

    def _get_all_scim_groups(self, config):
        result = []
        rows = []
        group_members = defaultdict(list)
        group_attr_map = config.get("group_attr_map", [])
        self.group_match_attr = "id"

        for item in group_attr_map:
            if item.get("target_attr") == "id":
                self.group_match_attr = item.get("source_attr")
                break

        conn = get_connection(config)
        cursor = self.get_cursor(config, conn)
        target_group_table = config.get("target_group_table")
        sql = f"select * from {target_group_table}"
        cursor.execute(sql)
        row = cursor.fetchone()
        while row:
            rows.append(row)
            parent_fk = config.get("group_table_parent_fk")
            if parent_fk:
                group_match_id = row.get(self.group_match_attr)
                # parent_id = row.get(parent_fk)
                parent_match_id = self._get_group_parent_match_id(
                    conn, config, row, parent_fk
                )
                if parent_match_id:
                    group_members[parent_match_id].append(group_match_id)
            row = cursor.fetchone()

        for group in rows:
            group_match_id = group.get(self.group_match_attr)
            members = group_members.get(group_match_id, [])
            scim_group = get_scim_group(group, members, group_attr_map)
            result.append(scim_group)
        conn.close()
        return result

    ############################################################################
    # AD Server: 获取User数据
    ############################################################################

    def _get_m2o_user_group(self, conn, config, user_row):
        user_table_group_fk = config.get("user_table_group_fk")
        target_group_table = config.get("target_group_table")
        group_id = user_row.get(user_table_group_fk.split(":")[0])
        if group_id:
            sql = f"select * from {target_group_table} where {user_table_group_fk.split(':')[1]} = %s"
            cursor = self.get_cursor(config, conn)
            cursor.execute(sql, (group_id,))
            group_row = cursor.fetchone()
            cursor.close()
            if group_row:
                group_match_id = group_row.get(self.group_match_attr)
                return [group_match_id]
            else:
                logger.error(f'No group record {group_id} found')
                return []

    def _get_m2m_user_groups(self, conn, config, user_row):
        """
        中间表user_group_rel_user_fk， user_group_rel_group_fk
        第一次查询: user_row[user_group_rel_user_fk.split(':')[1]] = user_group_rel_user_fk.split(':')[0]
                    结果为所有当前用户所属的group记录
        第二次查询：查询target_group_table 中所有的self.group_match_attr字段，匹配条件为：
                    user_group_rel_group_fk.split(':')[1] in 第一次查询中所有的记录的user_group_rel_group_fk.split(':')[0]字段
        """
        target_group_table = config.get("target_group_table")
        user_group_rel_table = config.get("user_group_rel_table")
        user_group_rel_user_fk = config.get("user_group_rel_user_fk")
        user_group_rel_group_fk = config.get("user_group_rel_group_fk")
        if not (user_group_rel_group_fk and user_group_rel_user_fk):
            return []
        cursor = self.get_cursor(config, conn)
        sql = f"select * from {user_group_rel_table} where { user_group_rel_user_fk.split(':')[0]} = %s"
        user_id = user_row[user_group_rel_user_fk.split(':')[1]]
        cursor.execute(sql, (user_id,))
        user_group_rels = cursor.fetchall()
        if not user_group_rels:
            return []
        all_group_ids = [
            item[user_group_rel_group_fk.split(':')[0]] for item in user_group_rels
        ]
        all_groups_str = ",".join(["%s" for _ in all_group_ids])

        sql = f"select * from {target_group_table} where {user_group_rel_group_fk.split(':')[1]} in ({all_groups_str})"
        cursor.execute(sql, tuple(all_group_ids))
        all_groups = cursor.fetchall()
        cursor.close()
        groups = [grp[self.group_match_attr] for grp in all_groups]
        return groups

    def _get_all_scim_users(self, config):
        result = []
        user_attr_map = config.get("user_attr_map", [])
        group_attr_map = config.get("user_attr_map", [])
        self.user_match_attr = "id"
        self.group_match_attr = "id"

        for item in user_attr_map:
            if item.get("target_attr") == "id":
                self.user_match_attr = item.get("source_attr")
                break

        for item in group_attr_map:
            if item.get("target_attr") == "id":
                self.group_match_attr = item.get("source_attr")
                break

        conn = get_connection(config)
        cursor = self.get_cursor(config, conn)
        target_user_table = config.get("target_user_table")
        sql = f"select * from {target_user_table}"
        cursor.execute(sql)
        row = cursor.fetchone()
        while row:
            user_table_group_fk = config.get("user_table_group_fk")
            user_group_rel_table = config.get("user_group_rel_table")

            if user_table_group_fk:
                groups = self._get_m2o_user_group(conn, config, row)
            elif user_group_rel_table:
                groups = self._get_m2m_user_groups(conn, config, row)
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
