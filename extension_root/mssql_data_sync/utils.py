from typing import Sized
from data_sync.models import DataSyncConfig
import pymssql
from scim_server.schemas.core2_enterprise_user import Core2EnterpriseUser
from scim_server.schemas.core2_group import Core2Group
from scim_server.protocol.path import Path
from scim_server.schemas.schema_identifiers import SchemaIdentifiers
from .constants import UserExtensionSchema, GroupExtensionSchema
from scim_server.utils import (
    compose_core2_user,
    compose_enterprise_extension,
    compose_core2_group,
    compose_core2_group_member,
)
from scim_server.schemas.member import Member


def load_config(tenant_uuid):
    config = DataSyncConfig.active_objects.filter(
        tenant__uuid=tenant_uuid,
        type="mssql_data_sync",
    ).first()

    if not config:
        return None
    return config


def get_connection(db_config):
    conn = pymssql.connect(
        db_config.get('server'),
        db_config.get('user'),
        db_config.get('password'),
        db_config.get('database'),
        port=db_config.get('port'),
    )
    return conn


def compose_custom_user_extension(user, scim_path, value):
    custom_extension = user.custom_extension
    if UserExtensionSchema not in custom_extension:
        user.add_custom_attribute(UserExtensionSchema, {})

    # if scim_path.attribute_path == 'FSTATUS':
    #     custom_extension[UserExtensionSchema]['FSTATUS'] = value
    # elif scim_path.attribute_path == 'FCOMP_ID':
    #     custom_extension[UserExtensionSchema]['FCOMP_ID'] = value
    # elif scim_path.attribute_path == 'FDEPT_ID':
    #     custom_extension[UserExtensionSchema]['FDEPT_ID'] = value
    # elif scim_path.attribute_path == 'FCOMP':
    #     custom_extension[UserExtensionSchema]['FCOMP'] = value
    custom_extension[UserExtensionSchema][scim_path.attribute_path] = value


def get_scim_user(value_dict, user_attr_map):
    user = Core2EnterpriseUser()
    for app_attr, value in value_dict.items():
        scim_attr_expression = user_attr_map.get(app_attr)
        if not scim_attr_expression:
            continue
        scim_path = Path.create(scim_attr_expression)
        if (
            scim_path.schema_identifier
            and scim_path.schema_identifier == SchemaIdentifiers.Core2EnterpriseUser
        ):
            compose_enterprise_extension(user, scim_path, value)
        elif (
            scim_path.schema_identifier
            and scim_path.schema_identifier == UserExtensionSchema
        ):
            compose_custom_user_extension(user, scim_path, value)
        else:
            compose_core2_user(user, scim_path, value)
    user.add_schema(UserExtensionSchema)
    return user


def compose_custom_group_extension(group, scim_path, value):
    custom_extension = group.custom_extension
    if GroupExtensionSchema not in custom_extension:
        group.add_custom_attribute(GroupExtensionSchema, {})

    if scim_path.attribute_path == 'FSTATUS':
        custom_extension[GroupExtensionSchema]['FSTATUS'] = value
    elif scim_path.attribute_path == 'FCOMP_ID':
        custom_extension[GroupExtensionSchema]['FCOMP_ID'] = value
    elif scim_path.attribute_path == 'FMANAGER':
        custom_extension[GroupExtensionSchema]['FMANAGER'] = value
    elif scim_path.attribute_path == 'FCOMP':
        custom_extension[GroupExtensionSchema]['FCOMP'] = value


def get_scim_group(value_dict, members, group_attr_map):
    group = Core2Group()
    group.members = []
    for app_attr, value in value_dict.items():
        scim_attr_expression = group_attr_map.get(app_attr)
        if not scim_attr_expression:
            continue
        scim_path = Path.create(scim_attr_expression)

        if (
            scim_path.schema_identifier
            and scim_path.schema_identifier == GroupExtensionSchema
        ):
            compose_custom_group_extension(group, scim_path, value)
        else:
            compose_core2_group(group, scim_path, value)

    for item in members:
        member = Member()
        for app_attr, value in item.items():
            scim_attr_expression = group_attr_map.get(app_attr)
            if not scim_attr_expression:
                continue
            scim_path = Path.create(scim_attr_expression)
            compose_core2_group_member(member, scim_path, value)
        group.members.append(member)
    group.add_schema(GroupExtensionSchema)
    return group
