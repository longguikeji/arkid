from typing import List
from django.shortcuts import render
from ninja import ModelSchema, Schema
from arkid.core.api import api
from arkid.core.models import Tenant
from arkid.core.translation import gettext_default as _


@api.get("/mine/tenant/{tenant_id}/apps/",tags=[_("我的")])
def get_mine_apps(request, tenant_id: str):
    """ 我的应用列表,TODO
    """
    return []

@api.get("/mine/tenant/{tenant_id}/profile/",tags=[_("我的")])
def get_mine_profile(request, tenant_id: str):
    """ 我的个人资料,TODO
    """
    return {}

@api.post("/mine/tenant/{tenant_id}/profile/",tags=[_("我的")])
def update_mine_profile(request, tenant_id: str):
    """ 更新我的个人资料,TODO
    """
    return {}

@api.get("/mine/tenant/{tenant_id}/permissions/",tags=[_("我的")])
def get_mine_permissions(request, tenant_id: str):
    """ 我的权限列表,TODO
    """
    return []

@api.post("/mine/tenant/{tenant_id}/permissions/",tags=[_("我的")])
def update_mine_permissions(request, tenant_id: str):
    """ 更新我的权限列表,TODO
    """
    return []

@api.get("/mine/tenant/{tenant_id}/all_permissions/",tags=[_("我的")])
def get_mine_all_permissions(request, tenant_id: str):
    """ 获取所有权限并附带是否已授权给我的状态,TODO
    """
    return []

@api.get("/mine/tenant/{tenant_id}/approves/",tags=[_("我的")])
def get_mine_approves(request, tenant_id: str):
    """ 我的审批列表，TODO
    """
    return []

@api.get("/mine/switch_tenant/{id}/",tags=[_("我的")],auth=None)
def get_mine_switch_tenant(request,tenant_id):
    """ 租户开关,TODO
    """
    context = {}
    tenant = Tenant.active_objects.get(id=tenant_id)
    context['tenant_id'] = tenant_id
    context['slug'] = tenant.slug
    
    return render(request,template_name='switch_tenant.html', context=context)

@api.get("/mine/logout/",tags=[_("我的")])
def get_mine_logout(request):
    """ 退出登录,TODO
    """
    return {}

class MineTenantsOut(ModelSchema):
    class Config:
        model = Tenant
        model_fields=["id","name","slug","icon"]

@api.get("/mine/tenants/",response=List[MineTenantsOut],tags=[_("我的")],auth=None)
def get_mine_tenants(request):
    """ 获取我的租户,TODO
    """
    tenants = Tenant.active_objects.all()
    return tenants