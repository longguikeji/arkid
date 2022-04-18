import json
import ldap3
from data_sync.models import DataSyncConfig
from ldap3 import Server, Connection
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
from common.logger import logger


def load_config(tenant_uuid):
    agent = DataSyncConfig.active_objects.filter(
        tenant__uuid=tenant_uuid,
        type="ad_data_sync_server",
    ).first()

    if not agent:
        return None
    data = agent.data
    return data


# def get_ldap_settings_from_config(**data):
#     user_attr_map = data.get("user_attr_map")
#     if isinstance(user_attr_map, str):
#         user_attr_map = json.loads(user_attr_map)
#     group_attr_map = data.get("group_attr_map")
#     if isinstance(group_attr_map, str):
#         group_attr_map = json.loads(group_attr_map)
#     settings = {
#         "LDAP_URL": data.get("server_uri"),
#         "LDAP_USE_TLS": data.get("use_tls"),
#         "LDAP_BIND_DN": data.get("bind_dn"),
#         "LDAP_BIND_PASSWORD": data.get("bind_password"),
#         "LDAP_USER_SEARCH_BASE": data.get("user_base_dn"),
#         "LDAP_GROUP_SEARCH_BASE": data.get("group_base_dn"),
#         "LDAP_USER_OBJECT_CLASS": data.get("user_object_class"),
#         "LDAP_GROUP_OBJECT_CLASS": data.get("group_object_class"),
#         "LDAP_USER_FIELDS": user_attr_map,
#         "LDAP_GROUP_FIELDS": group_attr_map,
#     }
#     ldap_settings = LDAPSettings(**settings)
#     return ldap_settings


def get_ad_connection(data):
    logger.info(f"Get AD Connection with config: {data}")
    host = data.get("host")
    port = data.get("port")
    use_tls = data.get("tls")
    bind_dn = data.get("bind_dn")
    bind_password = data.get("bind_password")
    server = Server(
        host=host,
        port=port,
        use_ssl=use_tls,
        get_info=ldap3.ALL,
        connect_timeout=data.get("connect_timeout"),
    )
    conn = Connection(
        server,
        user=bind_dn,
        password=bind_password,
        auto_bind=True,
        # raise_exceptions=False,
        receive_timeout=data.get("receive_timeout"),
    )
    return conn


def get_scim_group(value_dict, members, group_attr_map):
    # remove "{}" from objectGUID value
    value_dict["objectGUID"] = value_dict["objectGUID"].strip("{}")
    for m in members:
        m["objectGUID"] = m["objectGUID"].strip("{}")

    group = Core2Group()
    group.members = []
    for app_attr, value in value_dict.items():
        scim_attr_expression = group_attr_map.get(app_attr)
        if not scim_attr_expression:
            continue
        scim_path = Path.create(scim_attr_expression)
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
    return group


def get_scim_user(value_dict, user_attr_map):
    # remove "{}" from objectGUID value
    value_dict["objectGUID"] = value_dict["objectGUID"].strip("{}")
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
        else:
            compose_core2_user(user, scim_path, value)
    return user
