"""
LDAP Connection
"""

import logging
import ldap3
from django.db.models import Q
from tenant.models import Tenant
from inspect import getfullargspec
from django.contrib.auth import get_user_model
from django.forms.models import model_to_dict
from django_python3_ldap.utils import import_func, \
    format_search_filter, format_group_search_filter, \
    convert_model_fields_to_ldap_fields, convert_group_model_fields_to_ldap_fields

from inventory.models import Group

logger = logging.getLogger(__name__)


class LDAPConnection:
    """
    A connection to an LDAP server.
    """
    def __init__(self, settings, tenant=None):
        """
        Creates the LDAP connection.

        No need to call this manually, the `connection()` context
        manager handles initialization.
        """
        self.settings = settings

        self.connection = self.get_connection()

        self.tenant = tenant

    def get_connection(self):
        connection = ldap3.Connection(ldap3.Server(
            self.settings.LDAP_URL,
            allowed_referral_hosts=[("*", True)],
            get_info=ldap3.NONE,
            use_ssl=self.settings.LDAP_USE_TLS,
            connect_timeout=self.settings.LDAP_CONNECT_TIMEOUT,
        ),
                                      user=self.settings.LDAP_BIND_DN,
                                      password=self.settings.LDAP_BIND_PASSWORD,
                                      auto_bind=True,
                                      raise_exceptions=True,
                                      receive_timeout=self.settings.LDAP_RECEIVE_TIMEOUT)
        return connection

    def rebind(self):
        self.connection.rebind(self.settings.LDAP_BIND_DN, self.settings.LDAP_BIND_PASSWORD)

    def _get_user_dn(self, username):
        """
        get ldap dn of a django user object
        """
        kwargs = {'username': username}
        format_username = import_func(self.settings.LDAP_FORMAT_USERNAME)
        user_dn = format_username(self.settings, kwargs)
        return user_dn

    def _get_group_dn(self, groupname):
        """
        get ldap dn of a django group object
        """
        kwargs = {'name': groupname}
        format_username = import_func(self.settings.LDAP_FORMAT_GROUPNAME)
        group_dn = format_username(self.settings, kwargs)
        return group_dn

    def _get_user_data_from_ldap(self, username):
        kwargs = {'username': username}
        if self.connection.search(
                search_base=self.settings.LDAP_USER_SEARCH_BASE,
                search_filter=format_search_filter(self.settings, kwargs),
                search_scope=ldap3.SUBTREE,
                attributes=ldap3.ALL_ATTRIBUTES,
                get_operational_attributes=True,
                size_limit=1,
        ):
            return self.connection.response[0]
        else:
            return None

    def _get_group_data_from_ldap(self, groupname):
        kwargs = {'name': groupname}
        if self.connection.search(
                search_base=self.settings.LDAP_GROUP_SEARCH_BASE,
                search_filter=format_group_search_filter(self.settings, kwargs),
                search_scope=ldap3.SUBTREE,
                attributes=ldap3.ALL_ATTRIBUTES,
                get_operational_attributes=True,
                size_limit=1,
        ):
            return self.connection.response[0]
        else:
            return None

    def user_exists_in_ldap(self, username):
        if self._get_user_data_from_ldap(username):
            return True
        else:
            return False

    def group_exists_in_ldap(self, groupname):
        if self._get_group_data_from_ldap(groupname):
            return True
        else:
            return False

    def _get_or_create_user(self, user_data):
        """
        Returns a Django user for the given LDAP user data.

        If the user does not exist, then it will be created.
        """

        attributes = user_data.get("attributes")
        if attributes is None:
            logger.warning("LDAP user attributes empty")
            return None

        User = get_user_model()

        # Create the user data.
        user_fields = {
            field_name: (attributes[attribute_name][0] if isinstance(attributes[attribute_name],
                                                                     (list, tuple)) else attributes[attribute_name])
            for field_name, attribute_name in self.settings.LDAP_USER_FIELDS.items() if attribute_name in attributes
        }
        user_fields = import_func(self.settings.LDAP_CLEAN_USER_DATA)(user_fields)
        # Create the user lookup.
        user_lookup = {
            field_name: user_fields.pop(field_name, "")
            for field_name in self.settings.LDAP_USER_LOOKUP_FIELDS
        }

        # Search user in django db
        username = user_lookup['username']
        if self.tenant:
            if User.objects.filter(
                    ~Q(tenants__in=[self.tenant]),
                    username=username,
            ).exists():
                logger.info(f"user {username} conflict, {username} already in another tenant")
                return None

        # Update or create the user.
        user, created = User.objects.update_or_create(defaults=user_fields, **user_lookup)
        # If the user was created, set them an unusable password.
        if created:
            user.set_unusable_password()
            if self.tenant:
                user.tenants.add(self.tenant)
            user.save()
        # Update relations
        sync_user_relations_func = import_func(self.settings.LDAP_SYNC_USER_RELATIONS)
        sync_user_relations_arginfo = getfullargspec(sync_user_relations_func)
        args = {}    # additional keyword arguments
        for argname in sync_user_relations_arginfo.kwonlyargs:
            if argname == "connection":
                args["connection"] = self.connection
            elif argname == "dn":
                args["dn"] = user_data.get("dn")
            else:
                raise TypeError(f"Unknown kw argument {argname} in signature for LDAP_SYNC_USER_RELATIONS")
        # call sync_user_relations_func() with original args plus supported named extras
        sync_user_relations_func(user, attributes, **args)
        # All done!
        logger.info(f"LDAP user {user.username} lookup succeeded")
        return user

    def _get_or_create_group(self, group_data):
        """
        Returns a Django group for the given LDAP group data.

        If the group does not exist, then it will be created.
        """

        attributes = group_data.get("attributes")
        if attributes is None:
            logger.warning("LDAP group attributes empty")
            return None

        # Create the group data.
        group_fields = {
            field_name: (attributes[attribute_name][0] if isinstance(attributes[attribute_name],
                                                                     (list, tuple)) else attributes[attribute_name])
            for field_name, attribute_name in self.settings.LDAP_GROUP_FIELDS.items() if attribute_name in attributes
        }
        group_fields = import_func(self.settings.LDAP_CLEAN_GROUP_DATA)(group_fields)
        # Create the group lookup.
        group_lookup = {
            field_name: group_fields.pop(field_name, "")
            for field_name in self.settings.LDAP_GROUP_LOOKUP_FIELDS
        }

        # Search group in django db
        groupname = group_lookup['name']
        if self.tenant:
            if Group.objects.filter(
                    ~Q(tenant=self.tenant),
                    name=groupname,
            ).exists():
                logger.info(f"group {groupname} conflict, {groupname} already in another tenant")
                return None

        # Update or create the group.
        group, created = Group.objects.update_or_create(defaults=group_fields, **group_lookup)
        if created:
            if self.tenant:
                group.tenant = self.tenant
            group.save()
        # Update relations
        if 'member' in attributes:
            children = attributes['member']
            for child in children:
                if child:
                    # add user to the group
                    if self.settings.LDAP_USER_SEARCH_BASE in child:
                        username = child.split(',')[0] if ',' in child else child
                        username = username.split('=')[-1] if '=' in username else username
                        User = get_user_model()
                        try:
                            user = User.objects.get(username=username)
                            user.groups.add(group)
                            user.save()
                            logger.info(f'add user {username} to group {group.name}')
                        except:
                            pass
                    # add child group to the group
                    if self.settings.LDAP_GROUP_SEARCH_BASE in child:
                        groupname = child.split(',')[0] if ',' in child else child
                        groupname = groupname.split('=')[-1] if '=' in groupname else groupname
                        try:
                            child_group = Group.objects.get(name=groupname)
                            child_group.parent = group
                            child_group.save()
                            logger.info(f'add group {groupname} to group {group.name}')
                        except:
                            pass

        # All done!
        logger.info(f"LDAP group {group.name} lookup succeeded")
        return group

    def get_user_from_ldap(self, username):
        """
        Returns the user with the given identifier.

        The user identifier should be keyword arguments matching the fields
        in self.settings.LDAP_USER_LOOKUP_FIELDS.
        """
        data = self._get_user_data_from_ldap(username)
        if data:
            return self._get_or_create_user(data)
        logger.warning("LDAP user lookup failed")
        return None

    def get_group_from_ldap(self, groupname):
        """
        Returns the user with the given identifier.

        The user identifier should be keyword arguments matching the fields
        in self.settings.LDAP_USER_LOOKUP_FIELDS.
        """
        # Search the LDAP database.
        data = self._get_user_data_from_ldap(groupname)
        if data:
            return self._get_or_create_group(data)
        logger.warning("LDAP user lookup failed")
        return None

    def add_users_from_ldap(self):
        """
        Returns an iterator of Django users that correspond to
        users in the LDAP database.
        """
        paged_entries = self.connection.extend.standard.paged_search(
            search_base=self.settings.LDAP_USER_SEARCH_BASE,
            search_filter=format_search_filter(self.settings, {}),
            search_scope=ldap3.SUBTREE,
            attributes=ldap3.ALL_ATTRIBUTES,
            get_operational_attributes=True,
            paged_size=30,
        )
        success_count, failed_count = 0, 0
        for entry in paged_entries:
            if entry["type"] == "searchResEntry":
                user = self._get_or_create_user(entry)
                if user:
                    success_count += 1
                    logger.info(f'synced user {user.username} from ldap')
                else:
                    failed_count += 1
        logger.info(f"synced {success_count} users from ldap success, {failed_count} users failed")

    def add_groups_from_ldap(self):
        """
        Returns an iterator of Django users that correspond to
        users in the LDAP database.
        """
        paged_entries = self.connection.extend.standard.paged_search(
            search_base=self.settings.LDAP_GROUP_SEARCH_BASE,
            search_filter=format_group_search_filter(self.settings, {}),
            search_scope=ldap3.SUBTREE,
            attributes=ldap3.ALL_ATTRIBUTES,
            get_operational_attributes=True,
            paged_size=30,
        )
        success_count, failed_count = 0, 0
        for entry in paged_entries:
            if entry["type"] == "searchResEntry":
                group = self._get_or_create_group(entry)
                if group:
                    success_count += 1
                    logger.info(f'synced group {group.name} from ldap')
                else:
                    failed_count += 1
        logger.info(f"synced {success_count} groups from ldap success, {failed_count} groups failed")

    def add_group_user_relation_from_ldap(self):
        # users and groups must already exist
        self.add_groups_from_ldap()
        logger.info("synced group and user relationship from ldap")

    def add_user_to_ldap(self, user):
        """
        Add user to ldap server.
        """
        username = user.username
        if self.user_exists_in_ldap(username):
            logger.info(f"user {username} already exists in ldap")
            return True

        user_dn = self._get_user_dn(username)
        object_class = self.settings.LDAP_USER_OBJECT_CLASS
        kwargs = model_to_dict(user)
        attributes = convert_model_fields_to_ldap_fields(self.settings, kwargs)
        if self.connection.add(dn=user_dn, object_class=object_class, attributes=attributes):
            logger.info(f"added user {username} to ldap")
            return True

        logger.info(f"add user {username} to ldap server failed: {self.connection.server}, \
                {user_dn}, {object_class}, {attributes}")
        return False

    def add_users_to_ldap(self):
        """
        Add all user to ldap server.
        """
        User = get_user_model()
        if self.tenant:
            users = User.objects.filter(tenants__in=[self.tenant])
        else:
            users = User.objects.all()

        success_count, failed_count = 0, 0
        for user in users:
            if self.add_user_to_ldap(user):
                success_count += 1
            else:
                failed_count += 1

        logger.info(f"add {success_count} users to ldap success, {failed_count} users failed")

    def add_group_to_ldap(self, group):
        """
        Add group to ldap server.
        """
        groupname = group.name
        if self.group_exists_in_ldap(groupname):
            logger.info(f"group {groupname} already exists in ldap")
            return True

        group_dn = self._get_group_dn(groupname)
        object_class = self.settings.LDAP_GROUP_OBJECT_CLASS
        kwargs = model_to_dict(group)
        attributes = convert_group_model_fields_to_ldap_fields(self.settings, kwargs)

        # get users of a group
        member = []
        users = group.user_set.all()
        for user in users:
            user_dn = self._get_user_dn(user.username)
            member.append(user_dn)

        # get child groups of a group
        children = group.children.all()
        for child in children:
            child_dn = self._get_group_dn(child.name)
            member.append(child_dn)

        attributes['member'] = member or ""

        if self.connection.add(dn=group_dn, object_class=object_class, attributes=attributes):
            logger.info(f"added group {groupname} to ldap")
            return True

        logger.info(f"add group {groupname} to ldap server failed: {self.connection.server}, \
                {group_dn}, {object_class}, {attributes}")
        return False

    def add_groups_to_ldap(self):
        """
        Add all groups to ldap server.
        """
        if self.tenant:
            groups = Group.objects.filter(tenant=self.tenant)
        else:
            groups = Group.objects.all()

        success_count, failed_count = 0, 0
        for group in groups:
            if self.add_group_to_ldap(group):
                success_count += 1
            else:
                failed_count += 1

        logger.info(f"add {success_count} groups to ldap success, {failed_count} groups failed")

    def add_group_user_relation_to_ldap(self):
        pass

    def add_user2group_member_to_ldap(self, username, groupname):
        """
        add user to group member in ldap server
        """
        group_data = self._get_group_data_from_ldap(groupname)
        if not group_data:
            logger.info(f"{groupname} does not exist in ldap")
            return

        user_data = self._get_group_data_from_ldap(username)
        if not user_data:
            logger.info(f"{username} does not exist in ldap")
            return

        user_dn = self._get_user_dn(username)
        if "attributes" in group_data and "member" in group_data["attributes"] and \
                user_dn in  group_data["attributes"]["member"]:
            logger.info(f"{username} already in {groupname} member in ldap")
            return

        group_dn = self._get_group_dn(groupname)
        self.connection.modify(group_dn, {'member': [(ldap3.MODIFY_ADD, [user_dn])]})
        logger.info(f"added {username} to {groupname} member in ldap")

    def add_group2group_member_to_ldap(self, child_groupname, parent_groupname):
        """
        add child group to group in ldap server
        """
        parent_group_data = self._get_group_data_from_ldap(parent_groupname)
        if not parent_group_data:
            logger.info(f"{parent_groupname} does not exist in ldap")
            return

        child_group_data = self._get_group_data_from_ldap(child_groupname)
        if not child_group_data:
            logger.info(f"{child_groupname} does not exist in ldap")
            return

        child_group_dn = self._get_user_dn(child_groupname)
        if "attributes" in parent_group_data and "member" in parent_group_data["attributes"] and \
                child_group_dn in parent_group_data["attributes"]["member"]:
            logger.info(f"{child_groupname} already in {parent_groupname} member in ldap")
            return

        parent_group_dn = self._get_group_dn(parent_groupname)
        self.connection.modify(parent_group_dn, {'member': [(ldap3.MODIFY_ADD, [child_group_dn])]})
        logger.info(f"added {child_groupname} to {parent_groupname} member in ldap")

    def remove_user2group_member_to_ldap(self, username, groupname):
        """
        remove user from group member in ldap server
        """
        group_data = self._get_group_data_from_ldap(groupname)
        if not group_data:
            logger.info(f"{groupname} does not exist in ldap")
            return

        user_data = self._get_group_data_from_ldap(username)
        if not user_data:
            logger.info(f"{username} does not exist in ldap")
            return

        user_dn = self._get_user_dn(username)
        if "attributes" in group_data and "member" in group_data["attributes"] and \
                user_dn not in group_data["attributes"]["member"]:
            logger.info(f"{username} not in {groupname} member in ldap")
            return

        group_dn = self._get_group_dn(groupname)
        self.connection.modify(group_dn, {'member': [(ldap3.MODIFY_DELETE, [user_dn])]})
        logger.info(f"removed {username} from {groupname} member in ldap")

    def delete_user_to_ldap(self, username):
        """
        detele user in ldap server 
        """
        if not self.user_exists_in_ldap(username):
            logger.info(f"user {username} does not exist in ldap server")
        dn = self._get_user_dn(username)
        self.connection.delete(dn)
        logger.info(f"delete user {username} in ldap server success")

    def delete_group_to_ldap(self, groupname):
        """
        delete group in ldap server
        """
        if not self.group_exists_in_ldap(groupname):
            logger.info(f"user {groupname} does not exist in ldap server")
        dn = self._get_user_dn(groupname)
        self.connection.delete(dn)
        logger.info(f"delete group {groupname} in ldap server success")

    def authenticate(self, username=None, password=None, **kwargs):
        """
        authenticate a user in ldap server
        """
        if not username or not password:
            return None
        dn = self._get_user_dn(username)
        if not self.connection.rebind(dn, password):
            return None
        self.rebind()
        user = self.get_user_from_ldap(username)
        return user
