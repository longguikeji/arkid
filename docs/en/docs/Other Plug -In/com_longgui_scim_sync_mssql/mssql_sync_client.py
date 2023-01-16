import re
import copy
import json
import datetime
from scim_server.protocol.path import Path
from arkid.common.logger import logger
from scim_server.schemas.comparison_operator import ComparisonOperator
from scim_server.utils import scim_obj_to_client_obj
import pymssql
from .utils import get_connection


class MssqlSyncClient:
    def __init__(self, config, groups, users):

        self.config = config

        self.user_attr_map = config.get('user_attr_map', [])
        self.group_attr_map = config.get('group_attr_map', [])
        self.user_match_attr = self.get_match_attr(self.user_attr_map)
        self.group_match_attr = self.get_match_attr(self.group_attr_map)

        self.users = users
        self.groups = groups

        self.conn = get_connection(config)

    def get_match_attr(self, attr_map):
        for item in attr_map:
            if item.get('source_attr') == "id":
                return item.get('target_attr')

    def exists_group(self, group_id: str):
        cursor = self.conn.cursor(as_dict=True)
        target_group_table = self.config.get("target_group_table")
        cursor.execute(
            f"select * from {target_group_table} where {self.group_match_attr} = %s",
            group_id,
        )
        row = cursor.fetchone()
        cursor.close()
        if not row:
            return False
        else:
            return True

    def add_group(self, group, parent_group):
        cursor = self.conn.cursor(as_dict=True)
        target_group_table = self.config.get("target_group_table")
        group_attr_map = self.config.get("group_attr_map")
        group_table_parent_fk = self.config.get("group_table_parent_fk")

        attr_map = [
            (m.get("source_attr"), m.get("target_attr")) for m in group_attr_map
        ]
        data = scim_obj_to_client_obj(group, attr_map)

        fields = list(data.keys())
        values = list(data.values())

        if group_table_parent_fk and parent_group:
            fields.append(group_table_parent_fk)
            values.append(parent_group.get("id"))

        fields_str = ','.join(fields)
        place_holders = ','.join(['%s' for f in fields])

        cursor.execute(f'SET IDENTITY_INSERT {target_group_table} ON')
        sql = (
            f"insert into {target_group_table} ({fields_str}) values ({place_holders})"
        )
        cursor.execute(sql, tuple(values))
        cursor.close()
        logger.info(f'ADD GROUP SUCCESS: {group["id"]}/{group["displayName"]}')

    def update_group(self, group, parent_group):
        cursor = self.conn.cursor(as_dict=True)
        target_group_table = self.config.get("target_group_table")
        group_attr_map = self.config.get("group_attr_map")
        group_table_parent_fk = self.config.get("group_table_parent_fk")

        attr_map = [
            (m.get("source_attr"), m.get("target_attr")) for m in group_attr_map
        ]
        data = scim_obj_to_client_obj(group, attr_map)

        values = []
        set_values = []
        for key, value in data.items():
            if key == self.group_match_attr:
                continue
            set_values.append(f"{key}=%s")
            values.append(value)

        if group_table_parent_fk and parent_group:
            set_values.append(f"{group_table_parent_fk}=%s")
            values.append(parent_group.get("id"))

        set_values_str = ','.join(set_values)
        sql = f"update {target_group_table} set {set_values_str} where {self.group_match_attr} = {group['id']}"
        cursor.execute(sql, tuple(values))
        cursor.close()
        logger.info(f'UPDATE GROUP SUCCESS: {group["id"]}/{group["displayName"]}')

    def get_root_groups(self):
        none_root_groups = set()
        for group in self.groups:
            # if group["status"] == "enabled":
            members = group.get("members", [])
            for member in members:
                none_root_groups.add(member["value"])

        root_groups = [
            group for group in self.groups if group["id"] not in none_root_groups
        ]
        return root_groups

    def sync_groups_from_root(self, group, parent_group=None):

        if not self.exists_group(group["id"]):
            self.add_group(group, parent_group)
        else:
            self.update_group(group, parent_group)

        parent_group = group
        for member in group.get("members", []):
            child_group_id = member["value"]
            child_group = self.group_dict[child_group_id]
            self.sync_groups_from_root(child_group, parent_group=parent_group)

    def sync_groups(self):
        logger.info(
            "========================= Syncing Groups ========================="
        )
        self.group_dict = {group["id"]: group for group in self.groups}

        # sync from root group to leaf group
        root_groups = self.get_root_groups()
        logger.info(f"root_groups found: {[group['id'] for group in root_groups]}")
        for root_group in root_groups:
            logger.info(f"syncing group from root_group: {root_group['id']}")
            self.sync_groups_from_root(root_group)

    def exists_user(self, user_id: str):
        cursor = self.conn.cursor(as_dict=True)
        target_user_table = self.config.get("target_user_table")
        cursor.execute(
            f"select * from {target_user_table} where {self.user_match_attr} = %s",
            user_id,
        )
        row = cursor.fetchone()
        cursor.close()
        if not row:
            return False
        else:
            return True

    def update_user_group_rel(
        self,
        user,
        groups,
        user_group_rel_table,
        user_group_rel_user_fk,
        user_group_rel_group_fk,
    ):
        cursor = self.conn.cursor(as_dict=True)
        cursor.execute(
            f"delete from {user_group_rel_table} where {user_group_rel_user_fk} = %s",
            user.get('id'),
        )
        values = []
        for group in groups:
            values.append((user.get('id'), group.get('value')))

        sql = f"insert into {user_group_rel_table}({user_group_rel_user_fk}, {user_group_rel_group_fk}) values(%s, %s)"
        cursor.executemany(sql, values)
        cursor.close()
        logger.info(f'UPDATE USER GROUP RELATION SUCCESS: {user["id"]}/{values}')

    def add_user(self, user):
        cursor = self.conn.cursor(as_dict=True)
        target_user_table = self.config.get("target_user_table")
        user_attr_map = self.config.get("user_attr_map")

        user_table_group_fk = self.config.get('user_table_group_fk')
        user_group_rel_table = self.config.get('user_group_rel_table')
        user_group_rel_user_fk = self.config.get('user_group_rel_user_fk')
        user_group_rel_group_fk = self.config.get('user_group_rel_group_fk')

        attr_map = [(m.get("source_attr"), m.get("target_attr")) for m in user_attr_map]
        data = scim_obj_to_client_obj(user, attr_map)

        fields = list(data.keys())
        values = list(data.values())

        groups = user.get("groups")
        if groups and user_table_group_fk:
            fields.append(user_table_group_fk)
            values.append(groups[0].get('value'))

        fields_str = ','.join(fields)
        place_holders = ','.join(['%s' for f in fields])

        cursor.execute(f'SET IDENTITY_INSERT {target_user_table} ON')
        sql = f"insert into {target_user_table} ({fields_str}) values ({place_holders})"
        cursor.execute(sql, tuple(values))
        cursor.close()

        # 处理user groups，可能存在第三方表，也可能不存在，直接再user表记录所属group
        if (
            groups
            and user_group_rel_table
            and user_group_rel_group_fk
            and user_group_rel_user_fk
        ):
            self.update_user_group_rel(
                user,
                groups,
                user_group_rel_table,
                user_group_rel_user_fk,
                user_group_rel_group_fk,
            )
        logger.info(f'ADD USER SUCCESS: {user["id"]}/{user["userName"]}')

    def update_user(self, user):
        cursor = self.conn.cursor(as_dict=True)
        target_user_table = self.config.get("target_user_table")
        user_attr_map = self.config.get("user_attr_map")

        user_table_group_fk = self.config.get('user_table_group_fk')
        user_group_rel_table = self.config.get('user_group_rel_table')
        user_group_rel_user_fk = self.config.get('user_group_rel_user_fk')
        user_group_rel_group_fk = self.config.get('user_group_rel_group_fk')

        attr_map = [(m.get("source_attr"), m.get("target_attr")) for m in user_attr_map]
        data = scim_obj_to_client_obj(user, attr_map)

        values = []
        set_values = []
        for key, value in data.items():
            if key == self.user_match_attr:
                continue
            set_values.append(f"{key}=%s")
            values.append(value)

        groups = user.get("groups")
        if groups and user_table_group_fk:
            set_values.append(f"{user_table_group_fk}=%s")
            values.append(groups[0].get('value'))

        set_values_str = ','.join(set_values)
        sql = f"update {target_user_table} set {set_values_str} where {self.user_match_attr} = {user['id']}"
        cursor.execute(sql, tuple(values))
        cursor.close()

        # 处理user groups，可能存在第三方表，也可能不存在，直接再user表记录所属group
        if (
            groups
            and user_group_rel_table
            and user_group_rel_group_fk
            and user_group_rel_user_fk
        ):
            self.update_user_group_rel(
                user,
                groups,
                user_group_rel_table,
                user_group_rel_user_fk,
                user_group_rel_group_fk,
            )
        logger.info(f'UPDATE USER SUCCESS: {user["id"]}/{user["userName"]}')

    def sync_users(self):
        logger.info("========================= Syncing Users =========================")
        self.user_dict = {user["id"]: user for user in self.users}

        # sync users
        for user in self.users:

            mssql_user = self.exists_user(user["id"])
            if not mssql_user:
                # add new user
                self.add_user(user)
            else:
                # update existing user
                self.update_user(user)

    def delete_users(self):
        logger.info("========================= Delete Users =========================")
        target_user_table = self.config.get("target_user_table")
        all_user_ids = self.user_dict.keys()
        all_user_str = ','.join(all_user_ids)

        sql = f'delete from {target_user_table} where {self.user_match_attr} not in ({all_user_str})'
        cursor = self.conn.cursor()
        cursor.execute(sql)
        cursor.close()

    def delete_groups(self):
        logger.info("========================= Delete Groups =========================")
        target_group_table = self.config.get("target_group_table")
        all_group_ids = self.group_dict.keys()
        all_group_str = ','.join(all_group_ids)

        sql = f'delete from {target_group_table} where {self.group_match_attr} not in ({all_group_str})'
        cursor = self.conn.cursor()
        cursor.execute(sql)
        cursor.close()

    def sync(self):
        try:
            self.sync_groups()
            self.sync_users()
            self.delete_users()
            self.delete_groups()
        except Exception as e:
            logger.exception(e)
        finally:
            self.conn.close()
