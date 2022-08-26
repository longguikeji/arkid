#!/usr/bin/env python3
import uuid

from scim_server.protocol.path import Path
from scim_server.schemas.address import Address
from scim_server.schemas.attribute_names import AttributeNames
from scim_server.schemas.electronic_mail_address import ElectroicMailAddress
from scim_server.schemas.name import Name
from scim_server.schemas.phone_number import PhoneNumber
from scim_server.schemas.role import Role
from scim_server.schemas.schema_identifiers import SchemaIdentifiers
from scim_server.schemas.extension_attribute_enterprise_user import (
    ExtensionAttributeEnterpriseUser,
)
from scim_server.schemas.manager import Manager
from scim_server.schemas.comparison_operator import ComparisonOperator


def try_get_request_identifier():
    return str(uuid.uuid1())


def compose_enterprise_extension(user, scim_path, value):
    if user.enterprise_extension:
        extension = user.enterprise_extension
    else:
        extension = ExtensionAttributeEnterpriseUser()
        user.enterprise_extension = extension
    if scim_path.attribute_path == 'manager':
        compose_manager(user, scim_path, value)
    elif scim_path.attribute_path == 'employeeNumber':
        extension.employeeNumber = value
    elif scim_path.attribute_path == 'costCenter':
        extension.costCenter = value
    elif scim_path.attribute_path == 'organization':
        extension.organization = value
    elif scim_path.attribute_path == 'division':
        extension.division = value
    elif scim_path.attribute_path == 'department':
        extension.department = value


def compose_manager(user, scim_path, value):
    if not scim_path.value_path:
        return
    extension = user.enterprise_extension
    if not extension.manager:
        extension.manager = Manager()
    if scim_path.value_path.attribute_path == 'displayName':
        extension.manager.displayName = value
    elif scim_path.value_path.attribute_path == 'value':
        extension.manager.value = value


def compose_core2_user(user, scim_path, value):
    if scim_path.attribute_path == 'id':
        user.id = value
    elif scim_path.attribute_path == 'active':
        user.active = bool(value)
    elif scim_path.attribute_path == 'addresses':
        compose_addresses(user, scim_path, value)
    elif scim_path.attribute_path == 'displayName':
        user.displayName = value
    elif scim_path.attribute_path == 'emails':
        compose_emails(user, scim_path, value)
    elif scim_path.attribute_path == 'externalId':
        user.externalId = value
    elif scim_path.attribute_path == 'name':
        compose_name(user, scim_path, value)
    elif scim_path.attribute_path == 'phoneNumbers':
        compose_phone_numbers(user, scim_path, value)
    elif scim_path.attribute_path == 'preferredLanguage':
        user.preferredLanguage = value
    elif scim_path.attribute_path == 'roles':
        compose_roles(user, scim_path, value)
    elif scim_path.attribute_path == 'title':
        user.title = value
    elif scim_path.attribute_path == 'userName':
        user.userName = value


def compose_roles(user, scim_path, value):
    if not scim_path.sub_attributes:
        return
    if not scim_path.value_path:
        return
    sub_attribute = scim_path.sub_attributes[0]
    if sub_attribute.attribute_path != 'type':
        return
    role = Role()
    role.type = sub_attribute.comparison_value
    role.value = value
    if user.roles:
        user.roles.append(role)
    else:
        user.roles = [role]


def compose_phone_numbers(user, scim_path, value):
    if not scim_path.sub_attributes:
        return
    if not scim_path.value_path:
        return
    sub_attribute = scim_path.sub_attributes[0]
    if sub_attribute.attribute_path != 'type':
        return
    if sub_attribute.comparison_value not in ['fax', 'work', 'mobile']:
        return
    phone = PhoneNumber()
    phone.type = sub_attribute.comparison_value
    phone.value = value
    if user.phone_numbers:
        user.phone_numbers.append(phone)
    else:
        user.phone_numbers = [phone]


def compose_name(user, scim_path, value):
    if not scim_path.value_path:
        return
    if not scim_path.value_path.attribute_path:
        return
    name = user.name
    if not name:
        name = Name()
        user.name = name
    if scim_path.value_path.attribute_path == 'familyName':
        name.familyName = value
    elif scim_path.value_path.attribute_path == 'givenName':
        name.givenName = value
    elif scim_path.value_path.attribute_path == 'formatted':
        name.formatted = value


def compose_emails(user, scim_path, value):
    if not scim_path.sub_attributes:
        return
    if not scim_path.value_path:
        return
    sub_attribute = scim_path.sub_attributes[0]
    if sub_attribute.attribute_path != 'type':
        return
    email = ElectroicMailAddress()
    email.type = sub_attribute.comparison_value
    email.value = value
    if user.emails:
        user.emails.append(email)
    else:
        user.emails = [email]


def compose_addresses(user, scim_path, value):
    if not scim_path.sub_attributes:
        return
    if not scim_path.value_path:
        return
    sub_attribute = scim_path.sub_attributes[0]
    if sub_attribute.attribute_path != 'type':
        return
    address = Address()
    address.type = sub_attribute.comparison_value
    if scim_path.value_path.attribute_path == AttributeNames.Country:
        address.country = value
    if scim_path.value_path.attribute_path == AttributeNames.Locality:
        address.locality = value
    if scim_path.value_path.attribute_path == AttributeNames.PostalCode:
        address.postalCode = value
    if scim_path.value_path.attribute_path == AttributeNames.Region:
        address.region = value
    if scim_path.value_path.attribute_path == AttributeNames.StreetAddress:
        address.streetAddress = value
    if scim_path.value_path.attribute_path == AttributeNames.Formatted:
        address.formatted = value
    if user.addresses:
        user.addresses.append(address)
    else:
        user.addresses = [address]


def compose_core2_group(group, scim_path, value):
    if scim_path.attribute_path == 'id':
        group.id = value
    elif scim_path.attribute_path == 'displayName':
        group.displayName = value


def compose_core2_group_member(member, scim_path, value):
    if scim_path.attribute_path == 'value':
        member.value = value
    elif scim_path.attribute_path == 'type':
        member.type = value
    elif scim_path.attribute_path == 'ref':
        member.ref = value


def scim_obj_to_client_obj(scim_obj, attr_map):
    """
    Params:
        attr_map: List[(scim_attr, app_attr)]
    """
    result = {}
    for scim_attr, app_attr in attr_map:
        value = scim_obj
        scim_path = Path.create(scim_attr)
        while scim_path:
            if scim_path.schema_identifier:
                key = ":".join(scim_path.schema_identifier, scim_path.attribute_path)
            else:
                key = scim_path.attribute_path
            value = value.get(key)
            if value is None:
                break

            if scim_path.sub_attributes:
                scim_filter = scim_path.sub_attributes[0]
                if scim_filter.filter_operator != ComparisonOperator.Equals:
                    continue
                value = filter(
                    lambda c: c[scim_filter.attribute_path]
                    == scim_filter.comparison_value,
                    value,
                )
                value = list(value)
                if value:
                    value = value[0]
                else:
                    value = None
                    break
            scim_path = scim_path.value_path
        result[app_attr] = value
    return result
