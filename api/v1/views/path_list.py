#!/usr/bin/env python3

from typing import List
from arkid.core.api import api, operation
from arkid.core.constants import *
from arkid.core.translation import gettext_default as _
from arkid.core import event
from ninja import Schema
from ninja.pagination import paginate
from arkid.core.pagenation import CustomPagination
from arkid.core.schema import ResponseSchema
from pydantic import Field


class PathListOut(ResponseSchema):
    data: List[str] = Field(default=[])


@api.get(
    "/tenant/{tenant_id}/path_list/",
    response=PathListOut,
    tags=["API Path列表"],
    # auth=None,
)
@operation(PathListOut, roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
def get_path_list(request, tenant_id: str):
    """Openapi path列表"""
    result = []
    schema = api.get_openapi_schema()
    for path in schema["paths"].keys():
        result.append(path)
    return {"data": result}
