from scim_server.protocol.path import Path
from arkid.common.logger import logger
from scim_server.utils import scim_obj_to_client_obj
from .utils import get_connection
import MySQLdb


class DBSyncClient:
    def __init__(self, config, sync_log, groups, users):

        self.config = config
        self.sync_log = sync_log

        self.db_type = config.get('db_type')
        self.user_attr_map = config.get('user_attr_map', [])
        self.group_attr_map = config.get('group_attr_map', [])
        self.user_match_attr = self.get_match_attr(self.user_attr_map)
        self.group_match_attr = self.get_match_attr(self.group_attr_map)

        self.users = users
        self.groups = groups

        self.conn = get_connection(config)

    def get_cursor(self):
        if self.db_type == 'mysql':
            return self.conn.cursor(MySQLdb.cursors.DictCursor)
        elif self.db_type == 'sqlserver':
            return self.conn.cursor(as_dict=True)
        else:
            raise Exception("Unsupported db type")

    def get_match_attr(self, attr_map):
        for item in attr_map:
            if item.get('source_attr') == "id":
                return item.get('target_attr')

    def exists_group(self, group_id: str):
        cursor = self.get_cursor()

        target_group_table = self.config.get("target_group_table")
        sql = f"select * from {target_group_table} where {self.group_match_attr} = %s"
        cursor.execute(sql, (group_id,))
        row = cursor.fetchone()
        cursor.close()
        if not row:
            return False
        else:
            return True

    def get_parent_group_identifier(
        self, cursor, scim_parent_group, target_group_table, group_table_parent_fk
    ):
        """
        通过scim_parent_group的id=group_match_attr查询到表记录，
        然后返回表记录中group_table_parent_fk.split(':')[1]字段的值
        """
        field = group_table_parent_fk.split(':')[1]
        sql = f"select {field} from {target_group_table} where {self.group_match_attr} = %s"
        cursor.execute(sql, (scim_parent_group['id'],))
        row = cursor.fetchone()
        if row:
            return row.get(field)
        else:
            logger.error(f'No parent record {scim_parent_group["id"]} found')
            return None

    def add_group(self, group, parent_group):
        cursor = self.get_cursor()
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
            # 获取数据库中parent_group关联的字段的值
            parent_group_identifier = self.get_parent_group_identifier(
                cursor, parent_group, target_group_table, group_table_parent_fk
            )
            if parent_group_identifier:
                fields.append(group_table_parent_fk.split(':')[0])
                values.append(parent_group_identifier)

        fields_str = ','.join(fields)
        place_holders = ','.join(['%s' for f in fields])

        # cursor.execute(f'SET IDENTITY_INSERT {target_group_table} ON')
        sql = (
            f"insert into {target_group_table} ({fields_str}) values ({place_holders})"
        )
        cursor.execute(sql, tuple(values))
        cursor.close()
        self.sync_log.groups_created += 1
        logger.info(f'ADD GROUP SUCCESS: {group["id"]}/{group["displayName"]}')

    def update_group(self, group, parent_group):
        cursor = self.get_cursor()
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
            # 获取数据库中parent_group关联的字段的值
            parent_group_identifier = self.get_parent_group_identifier(
                cursor, parent_group, target_group_table, group_table_parent_fk
            )
            if parent_group_identifier:
                set_values.append(f"{group_table_parent_fk.split(':')[0]}=%s")
                values.append(parent_group_identifier)

        set_values_str = ','.join(set_values)
        sql = f"update {target_group_table} set {set_values_str} where {self.group_match_attr} = %s"
        values.append(group['id'])
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
        cursor = self.get_cursor()
        target_user_table = self.config.get("target_user_table")
        cursor.execute(
            f"select * from {target_user_table} where {self.user_match_attr} = %s",
            (user_id,),
        )
        row = cursor.fetchone()
        cursor.close()
        if not row:
            return False
        else:
            return True

    def update_user_group_rel(
        self,
        scim_user,
        scim_groups,
        user_group_rel_table,
        user_group_rel_user_fk,
        user_group_rel_group_fk,
    ):
        """
        根据scim_user的id=user_match_attr获取scim_user在数据库中的记录
        根据记录获取user_group_rel_user_fk.split(':')[1]中间表关联用户表的字段的值
        根据这个值删除中间表中，所有的user_group_rel_user_fk.split(':')[0]登录这个值的记录

        然后再新增用户和组织之间的关系的记录
        首先获取每个scim_group 根据scim_group.get('value')=group_match_attr获取在数据库中的记录
        在记录中取user_group_rel_group_fk.split(':')[1]字段的值，这个值和上面用户的值组成一条记录插入
        中间表中
        """
        cursor = self.get_cursor()
        target_user_table = self.config.get("target_user_table")
        target_group_table = self.config.get("target_group_table")
        cursor.execute(
            f"select * from {target_user_table} where {self.user_match_attr} = %s",
            (scim_user['id'],),
        )
        row = cursor.fetchone()
        if not row:
            logger.error(f"No user find with {self.user_match_attr}: {scim_user['id']}")
            return
        user_identifier = row.get(user_group_rel_user_fk.split(':')[1])
        if not user_identifier:
            logger.error(
                f"User table record has no field named: {user_group_rel_user_fk.split(':')[1]}"
            )
            return

        # 删除原来用户和组之间的关系
        sql = f"delete from {user_group_rel_table} where {user_group_rel_user_fk.split(':')[0]} = %s"
        cursor.execute(sql, (user_identifier,))
        values = []
        for group in scim_groups:
            sql = (
                f"select * from {target_group_table} where {self.group_match_attr} = %s"
            )
            cursor.execute(sql, (group['value'],))
            row = cursor.fetchone()
            if not row:
                logger.error(
                    f"No user find with {self.user_match_attr}: {scim_user['id']}"
                )
                continue
            group_identifier = row.get(user_group_rel_group_fk.split(':')[1])
            if not group_identifier:
                logger.error(
                    f"Group table record has no field named: {user_group_rel_group_fk.split(':')[1]}"
                )
                continue
            values.append((user_identifier, group_identifier))

        sql = f"insert into {user_group_rel_table}({user_group_rel_user_fk.split(':')[0]}, {user_group_rel_group_fk.split(':')[0]}) values(%s, %s)"
        cursor.executemany(sql, values)
        cursor.close()
        logger.info(f'UPDATE USER GROUP RELATION SUCCESS: {scim_user["id"]}/{values}')

    def get_user_group_identifier(
        self, cursor, scim_group_value, target_group_table, user_table_group_fk
    ):
        """
        通过scim_group_value=group_match_attr查询到表记录，
        然后返回表记录中user_table_group_fk.split(':')[1]字段的值
        """
        field = user_table_group_fk.split(':')[1]
        sql = f"select {field} from {target_group_table} where {self.group_match_attr} = %s"
        cursor.execute(sql, (scim_group_value,))
        row = cursor.fetchone()
        if row:
            return row.get(field)
        else:
            logger.error(f'No user parent group record {scim_group_value} found')
            return None

    def add_user(self, user):
        cursor = self.get_cursor()
        target_user_table = self.config.get("target_user_table")
        target_group_table = self.config.get("target_group_table")
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
            user_group_identifier = self.get_user_group_identifier(
                cursor, groups[0].get("value"), target_group_table, user_table_group_fk
            )
            if user_group_identifier:
                fields.append(user_table_group_fk.split(':')[0])
                values.append(user_group_identifier)

        fields_str = ','.join(fields)
        place_holders = ','.join(['%s' for f in fields])

        # cursor.execute(f'SET IDENTITY_INSERT {target_user_table} ON')
        sql = f"insert into {target_user_table} ({fields_str}) values ({place_holders})"
        cursor.execute(sql, tuple(values))
        cursor.close()

        # 处理user groups，可能存在第三方表，也可能不存在，直接在user表记录所属group
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
        self.sync_log.users_created += 1
        logger.info(f'ADD USER SUCCESS: {user["id"]}/{user["userName"]}')

    def update_user(self, user):
        cursor = self.get_cursor()
        target_user_table = self.config.get("target_user_table")
        target_group_table = self.config.get("target_group_table")
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
            user_group_identifier = self.get_user_group_identifier(
                cursor, groups[0].get("value"), target_group_table, user_table_group_fk
            )
            if user_group_identifier:
                set_values.append(f"{user_table_group_fk.split(':')[0]}=%s")
                values.append(user_group_identifier)

        set_values_str = ','.join(set_values)
        sql = f"update {target_user_table} set {set_values_str} where {self.user_match_attr} = %s"
        values.append(user['id'])
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
        all_user_str = ','.join(["%s" for _ in all_user_ids])

        sql = f'delete from {target_user_table} where {self.user_match_attr} not in ({all_user_str})'
        cursor = self.conn.cursor()
        cursor.execute(sql, tuple(all_user_ids))
        self.sync_log.users_deleted = cursor.rowcount
        cursor.close()

    def delete_groups(self):
        logger.info("========================= Delete Groups =========================")
        target_group_table = self.config.get("target_group_table")
        all_group_ids = self.group_dict.keys()
        all_group_str = ','.join(["%s" for _ in all_group_ids])

        sql = f'delete from {target_group_table} where {self.group_match_attr} not in ({all_group_str})'
        cursor = self.conn.cursor()
        cursor.execute(sql, tuple(all_group_ids))
        self.sync_log.groups_deleted = cursor.rowcount
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
