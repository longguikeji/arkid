import json
from scim_server.schemas.core2_group import Core2Group
from scim_server.schemas.core2_enterprise_user import Core2EnterpriseUser
from scim_server.schemas.schema_identifiers import SchemaIdentifiers
from scim_server.protocol.path import Path
from scim_server.utils import (
    compose_core2_user,
    compose_enterprise_extension,
    compose_core2_group,
    compose_core2_group_member,
)
from scim_server.schemas.member import Member
from arkid.common.logger import logger
from scim_server.schemas.user_groups import UserGroup as ScimUserGroup
import random
import string
import pymssql


def get_connection(db_config):
    conn = pymssql.connect(
        db_config.get('server'),
        db_config.get('user'),
        db_config.get('password'),
        db_config.get('database'),
        port=db_config.get('port'),
        autocommit=True,
    )
    return conn


def get_scim_group(value_dict, members, group_attr_map):
    group = Core2Group(displayName='')
    for item in group_attr_map:
        app_attr = item.get("source_attr")
        scim_attr = item.get("target_attr")
        value = value_dict.get(app_attr)
        scim_path = Path.create(scim_attr)
        compose_core2_group(group, scim_path, value)

    for item in members:
        member = Member(value=item)
        group.members.append(member)
    return group


def get_scim_user(value_dict, groups, attr_map):
    scim_user = Core2EnterpriseUser(userName='', groups=[])
    for item in attr_map:
        app_attr = item.get("source_attr")
        scim_attr = item.get("target_attr")
        value = value_dict.get(app_attr)
        scim_path = Path.create(scim_attr)
        if (
            scim_path.schema_identifier
            and scim_path.schema_identifier == SchemaIdentifiers.Core2EnterpriseUser
        ):
            compose_enterprise_extension(scim_user, scim_path, value)
        else:
            compose_core2_user(scim_user, scim_path, value)
    for grp in groups:
        if grp:
            scim_user.groups.append(ScimUserGroup(value=grp))
    return scim_user
