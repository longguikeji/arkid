from typing import List
from django.shortcuts import render
from arkid.core.api import api, operation
from arkid.core.translation import gettext_default as _
from arkid.core.pagenation import CustomPagination
from arkid.core.models import App, Tenant, ApproveRequest, User
from arkid.core.constants import NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN
from ninja.pagination import paginate
from django.db.models import Q
from ..schema.mine import MineAppsOut, MineLogoutOut, MineTenantListItemOut, ProfileSchemaOut, ProfileSchemaIn, MineTenantListOut


@api.get("/mine/tenant/{tenant_id}/apps/", tags=["我的"], response=MineAppsOut)
@operation(roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
def get_mine_apps(request, tenant_id: str):
    """我的应用列表"""
    apps = App.active_objects.filter(Q(tenant=request.tenant) | Q(entry_permission__is_open=True))
    return {'data':list(apps)}



@api.get(
    "/mine/tenant/{tenant_id}/profile/",
    tags=["我的"],
    response=ProfileSchemaOut,
)
@operation(roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
def get_mine_profile(request, tenant_id: str):
    """我的个人资料"""
    user = request.user
    user = User.expand_objects.filter(id=user.id).first()
    return user


@api.post(
    "/mine/tenant/{tenant_id}/profile/",
    tags=["我的"],
    response=ProfileSchemaOut,
)
@operation(roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
def update_mine_profile(request, tenant_id: str, data: ProfileSchemaIn):
    """更新我的个人资料"""
    user = request.user
    for key,value in data.dict().items():
        setattr(user,key,value)
    user.save()
    return user


@api.get("/mine/tenant/{tenant_id}/permissions/", tags=["我的"])
@operation(roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
def get_mine_permissions(request, tenant_id: str):
    """我的权限列表,TODO"""
    return []


@api.post("/mine/tenant/{tenant_id}/permissions/", tags=["我的"])
@operation(roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
def update_mine_permissions(request, tenant_id: str):
    """更新我的权限列表,TODO"""
    return []


@api.get("/mine/tenant/{tenant_id}/all_permissions/", tags=["我的"])
@operation(roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
def get_mine_all_permissions(request, tenant_id: str):
    """获取所有权限并附带是否已授权给我的状态"""
    return []


from api.v1.schema.approve_request import (
    ApproveRequestListItemOut,
    ApproveRequestListOut,
)


@api.get(
    "/mine/tenant/{tenant_id}/approve_requests/",
    tags=["我的"],
    response=List[ApproveRequestListItemOut],
)
@operation(ApproveRequestListOut, roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(CustomPagination)
def get_mine_approve_requests(
    request, tenant_id: str, package: str = "", is_approved: str = ""
):
    """我的审批列表"""
    tenant = request.tenant
    requests = ApproveRequest.valid_objects.filter(
        user=request.user, action__tenant=tenant
    )
    if package:
        requests = requests.filter(action__extension__package=package)
    if is_approved == "true":
        requests = requests.exclude(status="wait")
    elif is_approved == "false":
        requests = requests.filter(status="wait")
    return requests


@api.get("/mine/switch_tenant/{id}/", tags=["我的"])
@operation(roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
def get_mine_switch_tenant(request, id):
    """租户切换"""
    context = {}
    tenant = Tenant.active_objects.get(id=id)
    context['tenant_id'] = id
    context['slug'] = tenant.slug

    return render(request, template_name='switch_tenant.html', context=context)


@api.get("/tenant/{tenant_id}/mine/logout/", response=MineLogoutOut, tags=["我的"])
@operation(roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
def get_mine_logout(request,tenant_id: str):
    """退出登录"""
    request.auth.delete()
    return {
        "refresh":True
    }

@api.get("/mine/tenants/", response=List[MineTenantListItemOut], tags=["我的"])
@operation(roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(CustomPagination)
def get_mine_tenants(request):
    """获取我的租户"""
    tenants = Tenant.active_objects.filter(users=request.user).all()
    return list(tenants)
 