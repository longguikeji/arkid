from common.logger import logger
from utils import get_connection


class SyncClient:
    def sync(self):
        pass


class SyncClientMssql(SyncClient):
    def __init__(self, **settings):
        self.users = settings['users']
        self.groups = settings['groups']
        self.emp_table = settings['emp_table']
        self.dept_table = settings['dept_table']
        self.conn = get_connection(settings)

    def _get_or_create_group(self, group):
        """
        If the group does not exist, then it will be created.
        """
        groupname = group['name']

        # Update or create the group
        parent_group_id = group.get('parent',{}).get('sql_group_id','')
        group_attributes = {'name': groupname, 'parent': parent_group_id}
        names = ','.join(group_attributes.keys())
        values = ','.join(group_attributes.values())
        cursor = self.conn.cursor(as_dict=True)
        cursor.execute(f"""
                        INSERT INTO {self.dept_table} ({names}) VALUES ({values})
                        ON DUPLICATE KEY UPDATE name={groupname}
                        """)
        group_id = cursor.lastrowid
        cursor.close()

        return group_id

    def _get_or_create_user(self, user):
        """
        If the user does not exist, then it will be created.
        """
        username = user['username']

        # Update or create the user
        group_id = user['group_id']
        group = self.group_dict.get(group_id)
        if group and group.get('sql_group_id'):
            user_group_id = group['sql_group_id']
        else:
            user_group_id = ''

        user_attributes = user['attributes']
        user_attributes['user_group_id'] = user_group_id
        names = ','.join(user_attributes.keys())
        values = ','.join(user_attributes.values())
        cursor = self.conn.cursor(as_dict=True)
        cursor.execute(f"""
                        INSERT INTO {self.emp_table} ({names}) VALUES ({values})
                        ON DUPLICATE KEY UPDATE username={username}
                        """)
        user_id = cursor.lastrowid
        cursor.close()

        return user_id

    def delete_group(self, group):
        logger.info(f"deleting group {group['id']}")
        groupname = group['groupname']

        cursor = self.conn.cursor(as_dict=True)
        cursor.execute(f"""
                        select * from {self.dept_table} where name={groupname}
                        """)
        row = cursor.fetchone()
        cursor.close()
        if not row:
            logger.warning(f"disabling group {group['id']}, but {group['id']} does not exist in database")
            return

        cursor = self.conn.cursor(as_dict=True)
        cursor.execute(f"""
                        delete from {self.dept_table} where name={groupname}
                        """)
        cursor.close()

    def disable_user(self, user):
        logger.info(f"disabling user: id {user['id']} name user['name']")
        username = user['username']

        cursor = self.conn.cursor(as_dict=True)
        cursor.execute(f"""
                        select * from {self.emp_table} where username={username}
                        """)
        row = cursor.fetchone()
        cursor.close()
        if not row:
            logger.warning(f"disabling user {user['id']}, but {user['id']} does not exist in database")
            return

        cursor = self.conn.cursor(as_dict=True)
        cursor.execute(f"""
                        delete from {self.emp_table} where username={username}
                        """)
        cursor.close()

    def get_root_groups(self):
        none_root_groups = set()
        for group in self.groups:
            if group['status'] == 'enabled':
                members = group.get('members',[])
                for member in members:
                    none_root_groups.add(member['value'])

        root_groups = [group for group in self.groups if group['status']=='enabled' and group['id'] not in none_root_groups]
        return root_groups

    def sync_groups_from_root(self, group, parent_group=None):
        if parent_group:
            group['parent'] = parent_group

        sql_group_id = self._get_or_create_group(group)
        group['sql_group_id'] = sql_group_id

        for member in group.get('members',[]):
            child_group_id = member['value']
            child_group = self.group_dict[child_group_id]
            if child_group['status'] == 'enabled':
                self.sync_groups_from_root(child_group, parent_group=group)

    def sync_groups(self):
        logger.info('syncing groups')
        self.group_dict = {group['id']: group for group in self.groups}

        # sync from root group to leaf group
        root_groups = self.get_root_groups()
        logger.info(f"root_groups found: {[group['id'] for group in root_groups]}")
        for root_group in root_groups:
            logger.info(f"syncing group from root_group: {root_group['id']}")
            self.sync_groups_from_root(root_group)

    def sync_users(self):
        logger.info('syncing users')
        self.user_dict = {user['id']: user for user in self.users}

        self.users.sort(key=lambda x:x['id'])

        # sync users
        for user in self.users:
            if user['status'] == 'enabled':
                arkid_user = self._get_or_create_user(user)
                user['sql_user_id'] = arkid_user

    def delete_users(self):
        logger.info('syncing disabled users')
        for user in self.users:
            if user['status'] == 'disabled':
                self.disable_user(user)

    def delete_groups(self):
        logger.info('syncing disabled groups')
        for group in self.groups:
            if group['status'] == 'disabled':
                self.delete_group(group)

    def sync(self):
        self.sync_groups()
        self.sync_users()
        self.delete_users()
        self.delete_groups()
