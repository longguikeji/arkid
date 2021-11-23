import json
import ldap3
from data_sync.models import DataSyncConfig
from ldap3 import Server, Connection


def load_config(tenant_uuid):
    config = DataSyncConfig.active_objects.filter(
        tenant__uuid=tenant_uuid,
        type="ad_data_sync_server",
    ).first()

    if not config:
        return None
    return config


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
    host = data.get('host')
    port = data.get('port')
    use_tls = data.get('tls')
    bind_dn = data.get('bind_dn')
    bind_password = data.get('bind_password')
    server = Server(
        host=host,
        port=port,
        use_ssl=use_tls,
        # get_info=ldap3.NONE,
        # connect_timeout=self.connect_timeout,
    )
    conn = Connection(
        server,
        user=bind_dn,
        password=bind_password,
        auto_bind=True,
        # raise_exceptions=False,
        # receive_timeout=self.receive_timeout,
    )
    return conn
