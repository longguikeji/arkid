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


ClientConfig = create_extension_schema(
    "ClientConfig",
    __file__,
    fields=[
        # ('sign_name', str, Field(title=_("Sign Name", "短信签名名称"))),
        # ('template_code', str, Field(title=_("Template Code", "短信模板CODE"))),
        # ('sms_up_extend_code', Optional[str], Field(title=_("Sms Up Extend Code", "上行短信扩展码"))),
        # ('out_id', Optional[str], Field(title=_("Out ID", "外部流水扩展字段"))),
    ],
    base_schema=BaseScimSyncClientSchema,
)

ServerConfig = create_extension_schema(
    "ServerConfig",
    __file__,
    fields=[
        # ('sign_name', str, Field(title=_("Sign Name", "短信签名名称"))),
        # ('template_code', str, Field(title=_("Template Code", "短信模板CODE"))),
        # ('sms_up_extend_code', Optional[str], Field(title=_("Sms Up Extend Code", "上行短信扩展码"))),
        # ('out_id', Optional[str], Field(title=_("Out ID", "外部流水扩展字段"))),
    ],
    base_schema=BaseScimSyncServerSchema,
)


class ScimSyncArkIDExtension(ScimSyncExtension):
    def load(self):
        self.register_scim_sync_schema('ArkID', ClientConfig, ServerConfig)
        super().load()

    def _get_arkid_user_attrs(self, user):
        active = user.get("active")
        if active is None:
            active = True

        return {
            "username": user.get("userName", ""),
            "is_active": active,
            "is_del": False,
        }

    def _get_arkid_user(self, scim_user, tenant, sync_log):
        scim_external_id = scim_user["id"]
        username = scim_user["userName"]
        arkid_user_attrs = self._get_arkid_user_attrs(scim_user)
        user_lookup = {
            "scim_external_id": scim_external_id,
            "username": username,
            "tenant": tenant,
        }
        # arkid_user, _ = User.objects.update_or_create(
        #     defaults=arkid_user_attrs, **user_lookup
        # )
        arkid_user = User.objects.filter(**user_lookup).first()
        if not arkid_user:
            user_lookup.update(arkid_user_attrs)
            arkid_user = User.objects.create(**user_lookup)
            sync_log.users_created += 1
        tenant.users.add(arkid_user)

        # 更新arkid_user所属的group
        arkid_user.usergroup_set.clear()
        for scim_group in scim_user.get("groups", []):
            scim_group_id = scim_group.get("value")
            arkid_group = self.scim_arkid_group_map.get(scim_group_id)
            if arkid_group:
                arkid_user.usergroup_set.add(arkid_group)
        # arkid_user.save()
        return arkid_user

    def _get_arkid_group(self, group, scim_arkid_map, tenant, sync_log):
        scim_external_id = group["id"] if "id" in group else group["value"]
        if scim_external_id not in scim_arkid_map:
            group_lookup = {"scim_external_id": scim_external_id, "tenant": tenant}
            arkid_group = UserGroup.objects.filter(**group_lookup).first()
            if not arkid_group:
                arkid_group = UserGroup.objects.create(**group_lookup)
                sync_log.groups_created += 1
            else:
                arkid_group.is_del = False
                arkid_group.is_active = True
            scim_arkid_map[scim_external_id] = arkid_group
            return arkid_group
        else:
            return scim_arkid_map[scim_external_id]

    def _sync_group_attr(self, arkid_group, scim_group):
        arkid_group.name = scim_group.get("displayName")
        arkid_group.save()

    def delete_group_from_root(self, root):
        logger.info(f"Delete Group {root.name} Start")
        children = root.children.all()
        if not children:
            root.delete()
            logger.info(f"delete group {root.name} success")
            return
        for item in children:
            self.delete_group_from_root(item)
        root.delete()
        logger.info(f"delete group {root.name} success")

    def sync_groups(self, groups, config, sync_log):
        """
        遍历groups中的SCIM 组织，逐一和ArkID中的组织匹配，如果不存在就创建，存在则更新，在此过程中
        同时遍历每个SCIM 组织中的members，同样的方式在ArkID中创建或更新组织，并且维护组织之间的父子关系，
        最后删除以前同步到ArkID但不在本次同步数据中的组织
        Args:
            groups (List): SCIM Server返回的组织列表
            config (arkid.extension.models.TenantExtensionConfig): Client模式创建的配置
        """
        logger.info("###### update&create groups ######")
        tenant = config.tenant
        self.scim_arkid_group_map = {}
        for group in groups:
            parent_group = self._get_arkid_group(
                group, self.scim_arkid_group_map, tenant, sync_log
            )
            self._sync_group_attr(parent_group, group)
            for member in group.get("members", []):
                sub_group = self._get_arkid_group(
                    member, self.scim_arkid_group_map, tenant, sync_log
                )
                sub_group.parent = parent_group

        logger.info("###### delete groups ######")
        groups_need_delete = (
            UserGroup.valid_objects.filter(tenant=config.tenant)
            .exclude(scim_external_id=None)
            .exclude(scim_external_id__in=self.scim_arkid_group_map.keys())
        )
        logger.info(f"******* groups to be deleted: {groups_need_delete} ********")
        root_groups = []
        for grp in groups_need_delete:
            if (grp.parent is None) or (grp.parent not in groups_need_delete):
                root_groups.append(grp)
        for root in root_groups:
            self.delete_group_from_root(root)
        delete_count = len(groups_need_delete)
        # groups_need_delete.delete()
        sync_log.groups_deleted = delete_count

    def sync_users(self, users, config, sync_log):
        """
        遍历users中的SCIM 用户记录，逐一和ArkID中的用户匹配，如果不存在匹配的就创建，存在则更新，
        最后删除以前同步到ArkID但不在本次同步数据中的用户
        Args:
            users (List): SCIM Server返回的用户列表
            config (arkid.extension.models.TenantExtensionConfig): Client模式创建的配置
        """
        logger.info("###### update&create users ######")
        tenant = config.tenant
        scim_user_ids = []
        for user in users:
            scim_user_ids.append(user["id"])
            try:
                arkid_user = self._get_arkid_user(user, tenant, sync_log)
            except IntegrityError as e:
                logger.error(e)
                logger.error(f"sync user failed: {user}")

        logger.info("###### delete users ######")
        users_need_delete = (
            tenant.users.filter(is_del=False)
            .exclude(scim_external_id=None)
            .exclude(scim_external_id__in=scim_user_ids)
        )
        logger.info(f"***** users to be deleted: {users_need_delete} ******")
        for u in users_need_delete:
            u.usergroup_set.clear()
            u.delete()
            sync_log.users_deleted += 1
            # users_need_delete.delete()

    def _get_scim_user(self, arkid_user):
        attr_map = {"id": "id", "username": "userName", "is_active": "active"}
        scim_user = Core2EnterpriseUser(userName='', groups=[])
        for arkid_attr, scim_attr in attr_map.items():
            value = getattr(arkid_user, arkid_attr)
            scim_path = Path.create(scim_attr)
            if (
                scim_path.schema_identifier
                and scim_path.schema_identifier == SchemaIdentifiers.Core2EnterpriseUser
            ):
                compose_enterprise_extension(scim_user, scim_path, value)
            else:
                compose_core2_user(scim_user, scim_path, value)

        # 生成用户所在的组
        parent_groups = arkid_user.usergroup_set.filter(is_del=0)
        for grp in parent_groups:
            scim_group = ScimUserGroup()
            scim_group.value = grp.id
            scim_group.display = grp.name
            scim_user.groups.append(scim_group)
        return scim_user

    def _get_scim_group(self, arkid_group):
        members = UserGroup.valid_objects.filter(parent=arkid_group)
        attr_map = {"id": "id", "name": "displayName"}
        scim_group = Core2Group(displayName='')
        for arkid_attr, scim_attr in attr_map.items():
            value = getattr(arkid_group, arkid_attr)
            scim_path = Path.create(scim_attr)
            compose_core2_group(scim_group, scim_path, value)
        for item in members:
            member = Member()
            member.value = item.id
            scim_group.members.append(member)
        return scim_group

    def _get_all_scim_users(self, tenant):
        scim_users = []
        arkid_users = User.valid_objects.filter(tenant=tenant)
        for arkid_user in arkid_users:
            scim_user = self._get_scim_user(arkid_user)
            scim_users.append(scim_user)
        return scim_users

    def _get_all_scim_groups(self, tenant):
        scim_groups = []
        arkid_groups = UserGroup.valid_objects.filter(tenant=tenant)
        for arkid_group in arkid_groups:
            scim_group = self._get_scim_group(arkid_group)
            scim_groups.append(scim_group)
        return scim_groups

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
        if not parameters.alternate_filters:
            all_users = self._get_all_scim_users(request.tenant)
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
        if not parameters.alternate_filters:
            groups = self._get_all_scim_groups(request.tenant)
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


extension = ScimSyncArkIDExtension()
