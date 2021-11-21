from common.logger import logger
from tenant.models import Tenant
from inventory.models import User, Group


class SyncClient:
    def sync(self):
        pass


class SyncClientArkID(SyncClient):
    def __init__(self, **settings):
        self.users = settings['users']
        self.groups = settings['groups']
        tenant_uuid = settings['tenant_uuid']
        tenant = Tenant.objects.filter(uuid=tenant_uuid).first()
        if not tenant:
            raise Exception(f"{tenant_uuid} does not exist")

    def _get_or_create_group(self, group):
        """
        Returns a Django group.
        If the group does not exist, then it will be created.
        """
        groupname = group['name']

        # Search group in django db
        if Group.objects.filter(
                ~Q(tenant=self.tenant),
                name=groupname,
        ).exists():
            raise Exception(f"group {groupname} conflict, {groupname} already in another tenant")

        # Update or create the group.
        group_lookup = {'name': groupname}
        arkid_group, created = Group.objects.update_or_create(defaults={}, **group_lookup)
        if created:
            arkid_group.tenant = self.tenant
            arkid_group.parent = group['parent']['arkid_group']
            arkid_group.save()

        return arkid_group

    def _get_or_create_user(self, user):
        """
        Returns a Django user.
        If the user does not exist, then it will be created.
        """
        username = user['username']

        # Search group in django db
        if User.objects.filter(
                ~Q(tenant=self.tenant),
                username=username,
        ).exists():
            raise Exception(f"user {username} conflict, {username} already in another tenant")

        # Update or create the user.
        user_attributes = user['attributes']
        user_lookup = {'username': username}
        arkid_user, created = User.objects.update_or_create(defaults=user_attributes, **user_lookup)
        # If the user was created, set them an unusable password.
        if created:
            arkid_user.parent = user['parent']['arkid_group']

            # set user password
            arkid_user.set_unusable_password()

            arkid_user.tenants.add(self.tenant)
            group_id = user['group_id']
            group = self.group_dict.get(group_id)
            if group and group.get('arkid_group'):
                arkid_user.groups.add(group['arkid_group'])
            arkid_user.save()

        return arkid_user

    def delete_group(self, group):
        logger.info(f"deleting group {group['id']}")
        groupname = group['groupname']
        arkid_group = Group.objects.filter(name=groupname, tenant=self.tenant).first()
        if not arkid_group:
            logger.warning(f"disabling group {group['id']}, but {group['id']} does not exist in ldap")
            return

        arkid_group.is_del = True
        arkid_group.save()

    def disable_user(self, user):
        logger.info(f"disabling user: id {user['id']} name user['name']")
        username = user['username']
        arkid_user = User.objects.filter(username=username, tenant=self.tenant).first()
        if not arkid_user:
            logger.warning(f"disabling user {user['id']}, but {user['id']} does not exist in ldap")
            return

        arkid_user.is_del = True
        arkid_user.save()

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

        arkid_group = self._get_or_create_group(group)
        group['arkid_group'] = arkid_group

        for member in group.get('members',[]):
            child_group_id = member['value']
            child_group = self.group_dict[child_group_id]
            if child_group['status'] == 'enabled':
                self.sync_groups_from_root(child_group, parent_group=arkid_group)

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
                user['arkid_user'] = arkid_user

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
