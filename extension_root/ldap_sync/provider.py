from django_python3_ldap.ldap import LDAPConnection
from common.provider import AuthorizationAgentProvider
from .utils import load_config, get_ldap_settings_from_config

from . import signals


class LDAPSyncAgentProvider(AuthorizationAgentProvider):
    def __init__(self) -> None:
        super().__init__()

    def create(self, tenant_uuid, authorization_agent, data):
        server_uri = data.get("server_uri")
        bind_dn = data.get("bind_dn")
        bind_password = data.get("bind_password")
        user_base_dn = data.get("user_base_dn")
        group_base_dn = data.get("group_base_dn")
        user_object_class = data.get("user_object_class")
        group_object_class = data.get("group_object_class")
        user_attr_map = data.get("user_attr_map")
        group_attr_map = data.get("group_attr_map")
        use_tls = data.get("use_tls")

        return {
            "server_uri": server_uri,
            "bind_dn": bind_dn,
            "bind_password": bind_password,
            "user_base_dn": user_base_dn,
            "group_base_dn": group_base_dn,
            "user_object_class": user_object_class,
            "group_object_class": group_object_class,
            "user_attr_map": user_attr_map,
            "group_attr_map": group_attr_map,
            "use_tls": use_tls,
        }
