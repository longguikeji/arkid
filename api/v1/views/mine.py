from ninja import Schema, Query, ModelSchema
from arkid.core.api import api, operation
from arkid.core.translation import gettext_default as _


@api.get("/tenant/{tenant_id}/mine/apps/",tags=[_("我的")])
def get_mine_apps(request, tenant_id: str):
    """ 我的应用列表,TODO
    """
    return []

@api.get("/tenant/{tenant_id}/mine/profile/",tags=[_("我的")])
def get_mine_profile(request, tenant_id: str):
    """ 我的个人资料,TODO
    """
    return {}

@api.get("/tenant/{tenant_id}/mine/permissions/",tags=[_("我的")])
def get_mine_permissions(request, tenant_id: str):
    """ 我的权限列表,TODO
    """
    return []

@api.get("/tenant/{tenant_id}/mine/approves/",tags=[_("我的")])
def get_mine_approves(request, tenant_id: str):
    """ 我的审批列表，TODO
    """
    return []

@api.get("/tenant/{tenant_id}/mine/switch_tenant/",tags=[_("我的")])
def get_mine_switch_tenant(request, tenant_id: str):
    """ 租户开关,TODO
    """
    return {}

@api.get("/tenant/{tenant_id}/mine/logout/",tags=[_("我的")])
def get_mine_logout(request, tenant_id: str):
    """ 退出登录,TODO
    """
    return {}