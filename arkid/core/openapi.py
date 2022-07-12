from typing import Optional
from collections import defaultdict
from ninja.openapi import get_schema
from ninja.openapi.schema import OpenAPISchema
from arkid.core import routers, pages, translation, actions
from arkid.core.constants import *

import copy

def get_openapi_schema(self, path_prefix: Optional[str] = None) -> OpenAPISchema:
    if path_prefix is None:
        path_prefix = self.root_path
    schema = get_schema(api=self, path_prefix=path_prefix)
    schema["routers"] = routers.get_global_routers()
    schema["pages"] = pages.get_global_pages()
    # schema["navs"] = actions.get_nav_actions()
    # 直接从system permission表里拿，拿出来去拼
    # permissions = get_permissions(self)
    # schema["permissions"] = permissions
    import_permission(schema)
    schema["translation"] = translation.lang_maps
    
    return schema

def import_permission(scheme):
    from arkid.core.models import SystemPermission
    systempermissions = SystemPermission.valid_objects.order_by('sort_id')
    permissions = []
    for systempermission in systempermissions:
        item = {
            'name': systempermission.name,
            'sort_id': systempermission.sort_id,
            'type': systempermission.category,
        }
        describe = systempermission.describe
        if systempermission.category == 'group':
            item['container'] = describe.get('sort_ids', [])
            parent = describe.get('parent', -1)
            if parent != -1:
                item['parent'] = parent
        else:
            item['container'] = []
            item['operation_id'] = systempermission.operation_id
        permissions.append(item)
    scheme["permissions"] = permissions

roles = [
    {
        "name": NORMAL_USER,
        "sort_id": 0,
        "type": "group",
    },
    {
        "name": TENANT_ADMIN,
        "sort_id": 1,
        "type": "group",
    },
    {
        "name": PLATFORM_USER,
        "sort_id": 2,
        "type": "group",
    },
    {
        "name": PLATFORM_ADMIN,
        "sort_id": 3,
        "type": "group",
    },
]

def get_permissions(api):
    permissions = []
    groups = copy.deepcopy(roles)
    group_container = defaultdict(list)
    max_group = max(groups, key=lambda x: x["sort_id"])
    sort_id = max_group["sort_id"] + 1
    for prefix, router in api._routers:
        for path, path_view in router.path_operations.items():
            for op in path_view.operations:
                if not hasattr(op.view_func, "arkid_extension"):
                    continue
                permission = get_permission(api, op, group_container, sort_id)
                sort_id += 1
                permissions.append(permission)

    for group in groups:
        if group["name"] in group_container:
            group["container"] = group_container[group["name"]]
    return groups + permissions


def get_permission(api, operation, group_container, sort_id):
    permission = {}
    op_roles = operation.view_func.arkid_extension.get("roles", [])
    for role in op_roles:
        group_container[role].append(sort_id)

    op_id = operation.operation_id or api.get_openapi_operation_id(operation)
    # 取得请求地址和方式
    method = operation.methods[0]
    url = get_path(api, operation)
    name = operation.view_func.arkid_extension.get("name")
    if not name:
        description = operation.description
        name = description.replace("\n", "").strip()
    permission["name"] = name
    permission["method"] = method
    permission["url"] = url
    permission["sort_id"] = sort_id
    permission["type"] = operation.view_func.arkid_extension.get("type", "api")
    permission["operation_id"] = op_id

    return permission

def get_path(api, operation):
    '''
    获取一个解析后的路径
    '''
    root_path = api.root_path
    root_path = root_path[1:len(root_path)-1]
    url = root_path+operation.path
    return url
