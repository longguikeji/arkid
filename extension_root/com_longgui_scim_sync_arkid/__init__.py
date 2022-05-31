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

package = 'com.longgui.scim.sync.arkid'


ClientConfig = create_extension_schema(
    "ClientConfig",
    package,
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
    package,
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
        self.register_scim_sync_schema(self.type, ClientConfig, ServerConfig)
        super().load()

    def _get_arkid_user_attrs(self, user):
        return {
            "username": user.get("userName", ""),
            "is_active": user.get("active", True),
        }

    def _get_arkid_user(self, scim_user, tenant):
        scim_external_id = scim_user["id"]
        username = scim_user["userName"]
        arkid_user_attrs = self._get_arkid_user_attrs(scim_user)
        user_lookup = {
            "scim_external_id": scim_external_id,
            "tenant": tenant,
            "username": username,
        }
        arkid_user, _ = User.objects.update_or_create(
            defaults=arkid_user_attrs, **user_lookup
        )
        # 更新arkid_user所属的group
        arkid_user.user_set.clear()
        for scim_group in scim_user.get("groups", []):
            scim_group_id = scim_group.get("value")
            arkid_group = self.scim_arkid_group_map.get(scim_group_id)
            if arkid_group:
                arkid_user.user_set.add(arkid_group)
        arkid_user.save()
        return arkid_user

    def _get_arkid_group(self, group, scim_arkid_map, tenant):
        scim_external_id = group["id"] if "id" in group else group["value"]
        if scim_external_id not in scim_arkid_map:
            group_lookup = {"scim_external_id": scim_external_id, "tenant": tenant}
            arkid_group, _ = UserGroup.objects.update_or_create(**group_lookup)
            scim_arkid_map[scim_external_id] = arkid_group
            return arkid_group
        else:
            return scim_arkid_map[scim_external_id]

    def _sync_group_attr(self, arkid_group, scim_group):
        arkid_group.name = scim_group.get("displayName")
        arkid_group.save()

    def sync_groups(self, groups, config):
        logger.info("###### update&create groups ######")
        tenant = config.tenant
        self.scim_arkid_group_map = {}
        for group in groups:
            parent_group = self._get_arkid_group(
                group, self.scim_arkid_group_map, tenant
            )
            self._sync_group_attr(parent_group, group)
            for member in group.get("members", []):
                sub_group = self._get_arkid_group(
                    member, self.scim_arkid_group_map, tenant
                )
                sub_group.parent = parent_group

        logger.info("###### delete groups ######")
        groups_need_delete = (
            UserGroup.objects.filter(tenant=config.tenant)
            .exclude(scim_external_id=None)
            .exclude(scim_external_id__in=self.scim_arkid_group_map.keys())
        )
        logger.info(f"******* groups to be deleted: {groups_need_delete} ********")
        groups_need_delete.delete()

    def sync_users(self, users, config):
        logger.info("###### update&create users ######")
        tenant = config.tenant
        scim_user_ids = []
        for user in users:
            scim_user_ids.append(user["id"])
            try:
                arkid_user = self._get_arkid_user(user, tenant)
            except IntegrityError as e:
                logger.error(e)
                logger.error(f"sync user failed: {user}")

        logger.info("###### delete users ######")
        users_need_delete = (
            User.objects.filter(tenant=tenant)
            .exclude(scim_external_id=None)
            .exclude(scim_external_id__in=scim_user_ids)
        )
        logger.info(f"***** users to be deleted: {users_need_delete} ******")
        users_need_delete.delete()

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
        parent_groups = arkid_user.user_set.all()
        for grp in parent_groups:
            scim_user.groups.append(ScimUserGroup(value=grp.id.hex, display=grp.name))
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
            member = Member(value=item.id.hex)
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
        if not parameters.alternate_filters:
            all_users = self._get_all_scim_users(request.tenant)
            return all_users

    def query_groups(self, request, parameters, correlation_identifier):
        if not parameters.alternate_filters:
            groups = self._get_all_scim_groups(request.tenant)
            return groups


extension = ScimSyncArkIDExtension(
    package=package,
    name='ArkID用户数据同步',
    version='1.0',
    labels='scim-sync-arkid',
    homepage='https://www.longguikeji.com',
    logo='',
    author='hanbin@jinji-inc.com',
)
