import json
import typing
from tasks.celery import app
from tenant.models import Tenant
from inventory.models import User, Group
from django_python3_ldap.ldap import LDAPConnection
from .utils import load_config, get_ldap_settings_from_config


class LDAPSyncStatus:

    Enabled = 0
    Disabled = 1


class LDAPSyncDirection:

    upstream = "upstream"
    downstream = "downstream"


@app.task
def ldap_sync_user(tenant_uuid: str, user_id: int, is_del: bool = False, direction=LDAPSyncDirection.downstream):
    """
    ldap_sync user
    """
    user = User.objects.get(id=user_id)

    tenant = Tenant.objects.get(uuid=tenant_uuid)

    data = load_config(tenant_uuid)
    if not data:
        print(f"{tenant_uuid} config data does not exist")
        return
    print(f"ldap settings: {json.dumps(data)}")

    settings = get_ldap_settings_from_config(**data)
    ldap_conn = LDAPConnection(settings=settings, tenant=tenant)

    # 只支持下游同步
    if direction == LDAPSyncDirection.upstream:
        return

    if is_del:
        ldap_conn.delete_user_to_ldap(user.username)
    else:
        ldap_conn.add_user_to_ldap(user)

    print("Synced {user.username} to ldap!")


@app.task
def ldap_sync_group(tenant_uuid: str, group_id: int, is_del: bool = False, direction=LDAPSyncDirection.downstream):
    """
    ldap_sync group
    """
    group = Group.objects.get(id=group_id)

    tenant = Tenant.objects.get(uuid=tenant_uuid)

    data = load_config(tenant_uuid)
    if not data:
        print(f"{tenant_uuid} config data does not exist")
        return
    print(f"ldap settings: {json.dumps(data)}")

    settings = get_ldap_settings_from_config(**data)
    ldap_conn = LDAPConnection(settings=settings, tenant=tenant)

    # 只支持下游同步
    if direction == LDAPSyncDirection.upstream:
        return

    if is_del:
        ldap_conn.delete_group_to_ldap(group.name)
    else:
        ldap_conn.add_group_to_ldap(group)

    print("Synced {group.name} to ldap!")


@app.task
def provision_user(tenant_uuid: str, user_id: int, is_del: bool = False):
    """
    add user or delete user in ldap server
    """
    ldap_sync_user(tenant_uuid, user_id, is_del)


@app.task
def provision_group(tenant_uuid: str, group_id: int, is_del: bool = False):
    """
    add user or delete group in ldap server
    """
    ldap_sync_group(tenant_uuid, group_id, is_del)


@app.task
def ldap_sync_user_group_member(tenant_uuid: str,
                                action: str,
                                user_id: int,
                                group_id: int,
                                direction=LDAPSyncDirection.downstream):
    """
    ldap_sync user and group member relation
    """
    user = User.objects.get(id=user_id)
    group = Group.objects.get(id=group_id)

    tenant = Tenant.objects.get(uuid=tenant_uuid)

    data = load_config(tenant_uuid)
    if not data:
        print(f"{tenant_uuid} config data does not exist")
        return
    print(f"ldap settings: {json.dumps(data)}")

    settings = get_ldap_settings_from_config(**data)
    ldap_conn = LDAPConnection(settings=settings, tenant=tenant)

    # 只支持下游同步
    if direction == LDAPSyncDirection.upstream:
        return

    if action == 'add':
        ldap_conn.add_user2group_member_to_ldap(user.username, group.name)
    elif action == 'remove':
        ldap_conn.remove_user2group_member_to_ldap(user.username, group.name)

    print("Synced {user.username} and {group.name} member to ldap!")


@app.task
def provision_user_groups_changed(tenant_uuid: str,
                                  action: str,
                                  user_id: int,
                                  group_set: set,
                                  direction=LDAPSyncDirection.downstream):
    '''
    同步的前提是User和Group已经同步到服务端
    '''
    user = User.objects.get(id=user_id)

    # 只支持下游同步
    if direction == LDAPSyncDirection.upstream:
        return

    if action == 'pre_clear':
        groups = user.groups.all()
        for group in groups:
            # requires ldap memberOf function
            return

    elif action == 'pre_add':
        for group_id in group_set:
            ldap_sync_user_group_member(tenant_uuid, 'remove', user_id, group_id)

    elif action == 'pre_remove':
        for group_id in group_set:
            ldap_sync_user_group_member(tenant_uuid, 'add', user_id, group_id)
