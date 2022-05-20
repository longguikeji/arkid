from typing import List
from django.shortcuts import render
from ninja import ModelSchema, Schema
from arkid.core.api import api, operation
from arkid.core.models import Tenant
from arkid.core.translation import gettext_default as _
from arkid.core.pagenation import CustomPagination
from arkid.core.schema import ResponseSchema
from arkid.core.models import ApproveAction, ApproveRequest


@api.get("/mine/tenant/{tenant_id}/apps/", tags=["我的"], auth=None)
def get_mine_apps(request, tenant_id: str):
    """我的应用列表,TODO"""
    return []


@api.get("/mine/tenant/{tenant_id}/profile/", tags=["我的"], auth=None)
def get_mine_profile(request, tenant_id: str):
    """我的个人资料,TODO"""
    return {}


@api.post("/mine/tenant/{tenant_id}/profile/", tags=["我的"], auth=None)
def update_mine_profile(request, tenant_id: str):
    """更新我的个人资料,TODO"""
    return {}


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

from .approve_request import ApproveRequestOut


@api.get(
    "/mine/tenant/{tenant_id}/approve_requests/",
    tags=["我的"],
    response=List[ApproveRequestOut],
    auth=None,
)
def get_mine_approve_requests(request, tenant_id: str, package: str):
    """我的审批列表，TODO"""
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
    """ 退出登录
    """
    # request.token.expire()
    return render(request,template_name='logout.html')

class MineTenantListItemOut(ModelSchema):
    class Config:
        model = Tenant
        model_fields = ["id", "name", "slug", "icon"]


class MineTenantListOut(ResponseSchema):
    data: List[MineTenantListItemOut]

@api.get("/mine/tenants/",response=MineTenantListOut,tags=["我的"],auth=None)
def get_mine_tenants(request):
    """获取我的租户,TODO"""
    tenants = Tenant.active_objects.all()
    return {"data":list(tenants)}
