"""
utils
"""

from django_python3_ldap.conf import LDAPSettings
from authorization_agent.models import AuthorizationAgent


def load_config(tenant_uuid):
    agent = AuthorizationAgent.active_objects.filter(
        tenant__uuid=tenant_uuid,
        type="ldap_auth",
    ).first()

    assert agent is not None
    data = agent.data
    return data


def get_ldap_settings_from_config(**data):
    settings = {
        "LDAP_URL": data.get("server_uri"),
        "LDAP_USE_TLS": data.get("use_tls"),
        "LDAP_BIND_DN": data.get("bind_dn"),
        "LDAP_BIND_PASSWORD": data.get("bind_password"),
        "LDAP_USER_SEARCH_BASE": data.get("user_base_dn"),
        "LDAP_USER_OBJECT_CLASS": data.get("user_object_class"),
        "LDAP_USER_FIELDS": data.get("user_attr_map"),
    }
    ldap_settings = LDAPSettings(**settings)
    return ldap_settings
