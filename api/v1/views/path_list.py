#!/usr/bin/env python3

from typing import List
from arkid.core.api import api, operation
from arkid.core.constants import *
from arkid.core.translation import gettext_default as _
from arkid.core import event
from ninja import Schema
from ninja.pagination import paginate
from arkid.core.pagenation import CustomPagination


class GetPathListOutItem(Schema):
    path: str


@api.get(
    "/tenant/{tenant_id}/path_list/",
    response=List[GetPathListOutItem],
    tags=["API Path列表"],
    auth=None,
)
@operation(List[GetPathListOutItem], roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
def get_path_list(request, tenant_id: str):
    """Openapi path列表"""
    result = []
    schema = api.get_openapi_schema()
    for path in schema["paths"].keys():
        result.append({"path": path})
    return result
