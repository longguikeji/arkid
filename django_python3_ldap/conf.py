"""
Settings for ldap
"""

import django.conf


class LDAPSettings:
    """
    This is a simple class to take the place of the global settings object. An
    instance will contain all of our settings as attributes, with default values
    if they are not specified by the configuration.
    """

    _prefix = "LDAP_"

    defaults = {
        "LDAP_URL": "ldap://localhost:389",
        "LDAP_USE_TLS": False,
        "LDAP_BIND_DN": None,
        "LDAP_BIND_PASSWORD": None,
        "LDAP_USER_SEARCH_BASE": "ou=people,dc=example,dc=com",
        "LDAP_GROUP_SEARCH_BASE": "ou=group,dc=example,dc=com",
        "LDAP_USER_OBJECT_CLASS": "inetOrgPerson",
        "LDAP_GROUP_OBJECT_CLASS": "groupOfNames",
        "LDAP_USER_FIELDS": {
            "username": "cn",
            "first_name": "givenName",
            "last_name": "sn",
            "email": "mail",
        },
        "LDAP_GROUP_FIELDS": {
            "name": "cn",
        },
        "LDAP_USER_LOOKUP_FIELDS": ("username", ),
        "LDAP_GROUP_LOOKUP_FIELDS": ("name", ),
        "LDAP_CLEAN_USER_DATA": "django_python3_ldap.utils.clean_user_data",
        "LDAP_CLEAN_GROUP_DATA": "django_python3_ldap.utils.clean_group_data",
        "LDAP_FORMAT_SEARCH_FILTERS": "django_python3_ldap.utils.format_search_filters",
        "LDAP_SYNC_USER_RELATIONS": "django_python3_ldap.utils.sync_user_relations",
        "LDAP_FORMAT_USERNAME": "django_python3_ldap.utils.format_username_openldap",
        "LDAP_FORMAT_GROUPNAME": "django_python3_ldap.utils.format_groupname_openldap",
        "LDAP_ACTIVE_DIRECTORY_DOMAIN": None,
        "LDAP_CONNECT_TIMEOUT": None,
        "LDAP_RECEIVE_TIMEOUT": None
    }

    def __init__(self, **kwargs):
        """
        Loads our settings from django.conf.settings, applying defaults for any
        that are omitted.
        """
        settings = self.defaults.copy()
        settings.update(kwargs)

        for name, default in settings.items():
            value = getattr(django.conf.settings, name, default)
            setattr(self, name, value)
