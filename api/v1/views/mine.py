from typing import List
from django.shortcuts import render
from ninja import ModelSchema, Schema
from arkid.core.api import api, operation
from arkid.core.models import Tenant
from arkid.core.translation import gettext_default as _
from arkid.core.pagenation import CustomPagination
from arkid.core.schema import ResponseSchema
from arkid.core.models import ApproveAction, ApproveRequest, User
from pydantic import Field
from arkid.core.constants import NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN
from ninja.pagination import paginate


@api.get("/mine/tenant/{tenant_id}/apps/", tags=["我的"], auth=None)
def get_mine_apps(request, tenant_id: str):
    """我的应用列表,TODO"""
    return []


class ProfileSchemaOut(ModelSchema):
    class Config:
        model = User
        model_fields = ['id', 'username', 'avatar']


class ProfileSchemaIn(Schema):
    avatar: str = Field(title=_('Name', '头像'), default='')


@api.get(
    "/mine/tenant/{tenant_id}/profile/",
    tags=["我的"],
    response=ProfileSchemaOut,
)
@operation(roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
def get_mine_profile(request, tenant_id: str):
    """我的个人资料"""
    user = request.user
    return user


@api.put(
    "/mine/tenant/{tenant_id}/profile/",
    tags=["我的"],
    response=ProfileSchemaOut,
)
@operation(roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
def update_mine_profile(request, tenant_id: str, data: ProfileSchemaIn):
    """更新我的个人资料"""
    user = request.user
    user.avatar = data.avatar
    user.save()
    return user


@api.get("/mine/tenant/{tenant_id}/permissions/", tags=["我的"], auth=None)
def get_mine_permissions(request, tenant_id: str):
    """我的权限列表,TODO"""
    return []


@api.post("/mine/tenant/{tenant_id}/permissions/", tags=["我的"], auth=None)
def update_mine_permissions(request, tenant_id: str):
    """更新我的权限列表,TODO"""
    return []


@api.get("/mine/tenant/{tenant_id}/all_permissions/", tags=["我的"], auth=None)
def get_mine_all_permissions(request, tenant_id: str):
    """获取所有权限并附带是否已授权给我的状态,TODO"""
    return []


from api.v1.schema.approve_request import (
    ApproveRequestListItemOut,
    ApproveRequestListOut,
)


@api.get(
    "/mine/tenant/{tenant_id}/approve_requests/",
    tags=["我的"],
    response=List[ApproveRequestListItemOut],
    auth=None,
)
@operation(ApproveRequestListOut)
@paginate(CustomPagination)
def get_mine_approve_requests(request, tenant_id: str, package: str):
    """我的审批列表"""
    tenant = request.tenant
    requests = ApproveRequest.valid_objects.filter(
        user=request.user, action__tenant=tenant
    )
    if package:
        requests = requests.filter(action__extension__package=package)
    return requests


@api.get("/mine/switch_tenant/{id}/", tags=["我的"], auth=None)
def get_mine_switch_tenant(request, id):
    """租户开关,TODO"""
    context = {}
    tenant = Tenant.active_objects.get(id=id)
    context['tenant_id'] = id
    context['slug'] = tenant.slug

    return render(request, template_name='switch_tenant.html', context=context)


@api.get("/mine/logout/", tags=["我的"], auth=None)
def get_mine_logout(request):
    """退出登录"""
    # request.token.expire()
    return render(request, template_name='logout.html')


class MineTenantListItemOut(ModelSchema):
    class Config:
        model = Tenant
        model_fields = ["id", "name", "slug", "icon"]


class MineTenantListOut(ResponseSchema):
    data: List[MineTenantListItemOut]


@api.get("/mine/tenants/", response=MineTenantListOut, tags=["我的"], auth=None)
def get_mine_tenants(request):
    """获取我的租户,TODO"""
    tenants = Tenant.active_objects.all()
    return {"data": list(tenants)}
