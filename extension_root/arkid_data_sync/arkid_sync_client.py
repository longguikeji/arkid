from common.logger import logger
from tenant.models import Tenant
from inventory.models import User, Group


class SyncClient:
    def sync(self):
        pass


class SyncClientArkID(SyncClient):
    def __init__(self, **settings):
        self.users = settings["users"]
        self.groups = settings["groups"]
        self.target_group = settings["target_group"]
        tenant_uuid = settings["tenant_uuid"]
        self.tenant = Tenant.objects.filter(uuid=tenant_uuid).first()
        if not self.tenant:
            raise Exception(f"{tenant_uuid} does not exist")

    def _get_or_create_group(self, group):
        """
        Returns a Django group.
        If the group does not exist, then it will be created.
        """
        groupname = group["name"]
        group_id = group["id"]

        # Search group in django db
        # if Group.objects.filter(
        #         ~Q(tenant=self.tenant),
        #         name=groupname,
        # ).exists():
        #     raise Exception(f"group {groupname} conflict, {groupname} already in another tenant")

        # Update or create the group.
        group_lookup = {"scim_external_id": group_id}
        arkid_group, created = Group.objects.update_or_create(
            defaults={"name": groupname}, **group_lookup
        )
        arkid_group.tenant = self.tenant
        if created:
            logger.info(f"CREATE GROUP: {group_id}/{groupname}")
        else:
            logger.info(f"UPDATE GROUP: {group_id}/{groupname}")
        if group.get("parent"):
            arkid_group.parent = group["parent"]["arkid_group"]
        arkid_group.save()
        return arkid_group

    def _get_or_create_user(self, user):
        """
        Returns a Django user.
        If the user does not exist, then it will be created.
        """
        external_user_id = user["id"]
        name = user["name"]

        # Search group in django db
        # if User.objects.filter(
        #         ~Q(tenant=self.tenant),
        #         username=username,
        # ).exists():
        #     raise Exception(f"user {username} conflict, {username} already in another tenant")

        # Update or create the user.
        user_attributes = user["attributes"]
        arkid_user = User.objects.filter(scim_external_id=external_user_id).first()
        if not arkid_user:
            arkid_user = User.valid_objects.create(**user_attributes)
            logger.info(f"CREATE USER: username {name} --> {user_attributes}")
            # set user password
            arkid_user.set_unusable_password()
            arkid_user.tenants.add(self.tenant)
        else:
            # 创建时username必须，更新时选择不更新username， username在用户AD登录时更新
            arkid_user.first_name = user_attributes["first_name"]
            arkid_user.last_name = user_attributes["last_name"]
            arkid_user.nickname = user_attributes["nickname"]
            arkid_user.email = user_attributes["email"]
            # arkid_user.employee_id = user_attributes["employee_id"]
            arkid_user.tenants.add(self.tenant)
            logger.info(f"UPDATE USER: username {name} --> {user_attributes}")
        group_id = user["group_id"]
        group = self.group_dict.get(group_id)
        if group and group.get("arkid_group"):
            arkid_user.groups.clear()
            arkid_user.groups.add(group["arkid_group"])
        else:
            arkid_user.groups.clear()
        arkid_user.save()

        return arkid_user

    def delete_group(self, group):
        logger.info(f"DELETING GROUP: {group['id']}")
        group_id = group["id"]
        arkid_group = Group.objects.filter(
            scim_external_id=group_id, tenant=self.tenant
        ).first()
        if not arkid_group:
            logger.warning(
                f"disabling group {group['id']}, but {group['id']} does not exist in arkid"
            )
            return

        arkid_group.is_del = True
        arkid_group.save()

    def disable_user(self, user):
        logger.info(f"DISABLING USER: id {user['id']},  name {user['name']}")
        employee_id = user["id"]
        arkid_user = User.objects.filter(employee_id=employee_id).first()
        if not arkid_user:
            logger.warning(
                f"disabling user {user['id']}, but {user['id']} does not exist in arkid"
            )
            return

        arkid_user.is_del = True
        arkid_user.save()

    def get_root_groups(self):
        none_root_groups = set()
        for group in self.groups:
            members = group.get("members", [])
            for member in members:
                none_root_groups.add(member["value"])

        root_groups = [
            group for group in self.groups if group["id"] not in none_root_groups
        ]
        return root_groups

    def sync_groups_from_root(self, group, parent_group=None):
        if parent_group:
            group["parent"] = parent_group

        arkid_group = self._get_or_create_group(group)
        group["arkid_group"] = arkid_group

        for member in group.get("members", []):
            child_group_id = member["value"]
            child_group = self.group_dict[child_group_id]
            # if child_group["status"] == "enabled":
            self.sync_groups_from_root(child_group, parent_group=group)

    def sync_groups(self):
        logger.info("####### syncing groups ######")
        self.group_dict = {group["id"]: group for group in self.groups}

        # sync from root group to leaf group
        root_groups = self.get_root_groups()
        logger.info(f"root_groups found: {[group['id'] for group in root_groups]}")
        # arkid_base_group, _ = Group.valid_objects.get_or_create(
        #     tenant=self.tenant, name="组织架构"
        # )
        # base_group = {"arkid_group": arkid_base_group}
        real_root_group = None
        if self.target_group:
            arkid_target_group = Group.valid_objects.filter(
                uuid=self.target_group
            ).first()
            if arkid_target_group:
                real_root_group = {"arkid_group": arkid_target_group}
        for root_group in root_groups:
            logger.info(f"syncing group from root_group: {root_group['id']}")
            self.sync_groups_from_root(root_group, real_root_group)
            # self.sync_groups_from_root(root_group, base_group)

    def sync_users(self):
        logger.info("###### syncing users ######")
        self.user_dict = {user["id"]: user for user in self.users}

        # self.users.sort(key=lambda x: x["id"])

        # sync users
        for user in self.users:
            # if user["status"] == "enabled":
            arkid_user = self._get_or_create_user(user)
            user["arkid_user"] = arkid_user

    def delete_users(self):
        """
        遍历数据库用户如果不在接口返回的用户里面删除
        """
        logger.info("###### syncing disabled users ######")
        all_external_ids = self.tenant.user_tenant_set.exclude(
            scim_external_id=None
        ).values_list("scim_external_id", flat=True)
        for external_id in all_external_ids:
            if external_id not in self.user_dict:
                arkid_user = User.objects.filter(scim_external_id=external_id).first()
                arkid_user.groups.clear()
                arkid_user.delete()
                logger.info(f"DELETING USER: {arkid_user.username}")
        # for user in self.users:
        #     if user["status"] == "disabled":
        #         self.disable_user(user)

    def delete_groups(self):
        """
        遍历数据库组如果不在接口返回的组里面删除
        """
        logger.info("###### syncing disabled groups ######")
        all_group_ids = (
            Group.valid_objects.filter(tenant=self.tenant)
            .exclude(scim_external_id=None)
            .values_list("scim_external_id", flat=True)
        )
        for group_id in all_group_ids:
            if group_id not in self.group_dict:
                arkid_group = Group.valid_objects.filter(
                    scim_external_id=group_id
                ).first()
                arkid_group.delete()
                logger.info(f"DELETING GROUP: {group_id}")

        # for group in self.groups:
        #     if group["status"] == "disabled":
        #         self.delete_group(group)

    def sync(self):
        self.sync_groups()
        self.sync_users()
        self.delete_users()
        self.delete_groups()
