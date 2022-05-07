from typing import Optional
from collections import defaultdict
from ninja.openapi import get_schema
from ninja.openapi.schema import OpenAPISchema
from arkid.core import routers, pages, translation, actions
from arkid.core.constants import NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN

import copy

def get_openapi_schema(self, path_prefix: Optional[str] = None) -> OpenAPISchema:
    if path_prefix is None:
        path_prefix = self.root_path
    schema = get_schema(api=self, path_prefix=path_prefix)
    schema["routers"] = routers.get_global_routers()
    schema["pages"] = pages.get_global_pages()
    # schema["navs"] = actions.get_nav_actions()
    # 直接从system permission表里拿，拿出来去拼
    permissions = get_permissions(self)
    schema["permissions"] = permissions
    
    schema["translation"] = translation.lang_maps
    
    return schema

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
        "name": PLATFORM_ADMIN,
        "sort_id": 2,
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
    name = operation.view_func.arkid_extension.get("name")
    if not name:
        description = operation.description
        name = description.replace("\n", "").strip()
    permission["name"] = name
    permission["sort_id"] = sort_id
    permission["type"] = operation.view_func.arkid_extension.get("type", "api")
    permission["operation_id"] = op_id

    return permission
