import json


def generate_app_payload(app):
    data = {
        'uuid': app.uuid.hex,
        'name': app.name,
        'url': app.url,
        'description': app.description,
        'type': app.type,
        'data': app.data,
    }
    return json.dumps(data)


def generate_user_payload(user):
    from inventory.models import UserTenantPermissionAndPermissionGroup
    groups = user.groups.all()
    if groups:
        groups_data = []
        for g in groups:
            groups_data.append({'uuid': g.uuid.hex, 'name': g.name})
    else:
        groups_data = []

    permissions = UserTenantPermissionAndPermissionGroup.valid_objects.filter(user=user).all()
    if permissions:
        permissions_data = []
        for perm in permissions:
            permissions_data.append({'name': perm.permissions.name, 'codename': perm.permissions.codename})
    else:
        permissions_data = []

    data = {
        'username': user.username,
        'email': user.email,
        'mobile': user.mobile,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'nickname': user.nickname,
        'country': user.country,
        'job_title': user.job_title,
        'avatar': user.avatar,
        'groups': groups_data,
        'user_permissions': permissions_data,
    }
    return json.dumps(data)


def generate_group_payload(group):
    parent = group.parent
    if parent:
        parent_data = {'uuid': parent.uuid.hex, 'name': parent.name}
    else:
        parent_data = None

    permissions = group.permissions.all()
    if permissions:
        permissions_data = []
        for perm in permissions:
            permissions_data.append({'name': perm.name, 'codename': perm.codename})
    else:
        permissions_data = []

    data = {
        'uuid': group.uuid.hex,
        'name': group.name,
        'is_active': group.is_active,
        'is_del': group.is_del,
        'parent': parent_data,
        'permissions': permissions_data,
    }
    return json.dumps(data)
