"""
Some useful LDAP utilities.
"""

import re
import binascii
from django.utils.encoding import force_text
from django.utils.module_loading import import_string


def import_func(func):
    if callable(func):
        return func
    elif isinstance(func, str):
        return import_string(func)
    raise AttributeError("Expected a function {0!r}".format(func))


def clean_ldap_name(name):
    """
    Transforms the given name into a form that
    won't interfere with LDAP queries.
    """
    return re.sub(
        r'[^a-zA-Z0-9 _\-.@:*]',
        lambda c: "\\" + force_text(binascii.hexlify(c.group(0).encode("latin-1", errors="ignore"))).upper(),
        force_text(name),
    )


def convert_model_fields_to_ldap_fields(settings, model_fields):
    """
    Converts a set of model fields into a set of corresponding
    LDAP fields.
    """
    return {
        settings.LDAP_USER_FIELDS[field_name]: field_value
        for field_name, field_value in model_fields.items() if field_name in settings.LDAP_USER_FIELDS and field_value
    }


def convert_group_model_fields_to_ldap_fields(settings, model_fields):
    """
    Converts a set of model fields into a set of corresponding
    LDAP fields.
    """
    return {
        settings.LDAP_GROUP_FIELDS[field_name]: field_value
        for field_name, field_value in model_fields.items() if field_name in settings.LDAP_GROUP_FIELDS and field_value
    }


def format_search_filter(settings, model_fields):
    """
    Creates an LDAP search filter for the given set of model
    fields.
    """
    ldap_fields = convert_model_fields_to_ldap_fields(settings, model_fields)
    ldap_fields["objectClass"] = settings.LDAP_USER_OBJECT_CLASS
    search_filters = import_func(settings.LDAP_FORMAT_SEARCH_FILTERS)(ldap_fields)
    return "(&{})".format("".join(search_filters))


def format_group_search_filter(settings, model_fields):
    """
    Creates an LDAP search filter for the given set of model
    fields.
    """
    ldap_fields = convert_group_model_fields_to_ldap_fields(settings, model_fields)
    ldap_fields["objectClass"] = settings.LDAP_GROUP_OBJECT_CLASS
    search_filters = import_func(settings.LDAP_FORMAT_SEARCH_FILTERS)(ldap_fields)
    return "(&{})".format("".join(search_filters))


def clean_user_data(model_fields):
    """
    Transforms the user data loaded from
    LDAP into a form suitable for creating a user.
    """
    return model_fields


def clean_group_data(model_fields):
    """
    Transforms the group data loaded from
    LDAP into a form suitable for creating a group.
    """
    return model_fields


def format_username_openldap(settings, model_fields):
    """
    Formats a user identifier into a username suitable for
    binding to an OpenLDAP server.
    """
    return "{user_identifier},{search_base}".format(
        user_identifier=",".join("{attribute_name}={field_value}".format(
            attribute_name=clean_ldap_name(field_name),
            field_value=clean_ldap_name(field_value),
        ) for field_name, field_value in convert_model_fields_to_ldap_fields(settings, model_fields).items()),
        search_base=settings.LDAP_USER_SEARCH_BASE,
    )


def format_groupname_openldap(settings, model_fields):
    """
    Formats a user identifier into a username suitable for
    binding to an OpenLDAP server.
    """
    return "{user_identifier},{search_base}".format(
        user_identifier=",".join("{attribute_name}={field_value}".format(
            attribute_name=clean_ldap_name(field_name),
            field_value=clean_ldap_name(field_value),
        ) for field_name, field_value in convert_group_model_fields_to_ldap_fields(settings, model_fields).items()),
        search_base=settings.LDAP_GROUP_SEARCH_BASE,
    )


def format_username_active_directory(settings, model_fields):
    """
    Formats a user identifier into a username suitable for
    binding to an Active Directory server.
    """
    username = model_fields["username"]
    if settings.LDAP_ACTIVE_DIRECTORY_DOMAIN:
        username = "{domain}\\{username}".format(
            domain=settings.LDAP_ACTIVE_DIRECTORY_DOMAIN,
            username=username,
        )
    return username


def format_username_active_directory_principal(settings, model_fields):
    """
    Formats a user identifier into a username suitable for
    binding to an Active Directory server.
    """
    username = model_fields["username"]
    if settings.LDAP_ACTIVE_DIRECTORY_DOMAIN:
        username = "{username}@{domain}".format(
            username=username,
            domain=settings.LDAP_ACTIVE_DIRECTORY_DOMAIN,
        )
    return username


def sync_user_relations(user, ldap_attributes, *, connection=None, dn=None):
    # do nothing by default
    pass


def format_search_filters(ldap_fields):
    return [
        "({attribute_name}={field_value})".format(
            attribute_name=clean_ldap_name(field_name),
            field_value=clean_ldap_name(field_value),
        ) for field_name, field_value in ldap_fields.items()
    ]
