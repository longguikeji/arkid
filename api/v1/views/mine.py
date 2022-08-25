from typing import List
from django.shortcuts import render
from arkid.core.api import GlobalAuth, api, operation
from arkid.core.error import ErrorCode, ErrorDict, SuccessDict
from arkid.core.translation import gettext_default as _
from arkid.core.pagenation import CustomPagination
from arkid.core.models import App, AppGroup, Message, Tenant, ApproveRequest, User
from arkid.core.constants import NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN
from ninja.pagination import paginate
from django.db.models import Q
from ..schema.mine import *


@api.get("/mine/tenant/{tenant_id}/apps/", tags=["我的"], response=MineAppsOut)
@operation(roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
def get_mine_apps(request, tenant_id: str):
    """我的应用列表"""
    apps = App.active_objects.filter(
        Q(tenant=request.tenant) | Q(entry_permission__is_open=True)
    )
    return {'data': list(apps)}


@api.get(
    "/mine/tenant/{tenant_id}/profile/",
    tags=["我的"],
    response=ProfileSchemaFinalOut,
)
@operation(roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
def get_mine_profile(request, tenant_id: str):
    """我的个人资料"""
    real_user = request.user
    user = User.expand_objects.filter(id=real_user.id).first()
    user["tenant"] = real_user.tenant
    return SuccessDict(
        data=user
    )


@api.post(
    "/mine/tenant/{tenant_id}/profile/",
    tags=["我的"],
    response=ProfileSchemaOut,
)
@operation(roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
def update_mine_profile(request, tenant_id: str, data: ProfileSchemaIn):
    """更新我的个人资料"""
    user = request.user
    for key, value in data.dict().items():
        setattr(user, key, value)
    user.save()
    return user


@api.get(
    "/mine/tenant/{tenant_id}/permissions/",
    response=List[MinePermissionListSchemaOut],
    tags=["我的"],
)
@operation(roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(CustomPagination)
def get_mine_permissions(
    request,
    tenant_id: str,
    app_id: str = None,
    app_name: str = None,
    category: str = None,
):
    """我的权限列表"""
    login_user = request.user
    from arkid.core.perm.permission_data import PermissionData

    permissiondata = PermissionData()
    items = permissiondata.get_permissions_by_mine_search(
        tenant_id, app_id, None, None, login_user, app_name=app_name, category=category
    )
    return items


# @api.get("/mine/tenant/{tenant_id}/permissions/{permission_id}/open", tags=["我的"])
# @operation(roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
# def update_mine_permissions(request, tenant_id: str, permission_id: str, in_current: bool):
#     """更新我的权限列表"""
#     if in_current is False:
#         return ErrorDict(ErrorCode.PERMISSION_NOT_CLOSE)
#     # 需要申请更新权限列表

#     return {'error': ErrorCode.OK.value}


@api.get(
    "/mine/tenant/{tenant_id}/permissions/{permission_id}/add_permisssion", tags=['权限']
)
@operation(roles=[NORMAL_USER])
def mine_add_permission(request, tenant_id: str, permission_id: str):
    '''
    添加用户权限
    '''
    from arkid.core.event import Event, dispatch_event
    from arkid.core.event import ADD_USER_MANY_PERMISSION

    user = request.user
    if user:
        dispatch_event(
            Event(
                tag=ADD_USER_MANY_PERMISSION,
                tenant=request.tenant,
                request=request,
                data={
                    'user_ids': [str(user.id)],
                    'tenant_id': tenant_id,
                    'data_arr': [permission_id],
                },
            )
        )
    return {'error': ErrorCode.OK.value}


# @api.get("/mine/tenant/{tenant_id}/all_permissions/", tags=["我的"])
# @operation(roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
# def get_mine_all_permissions(request, tenant_id: str):
#     """获取所有权限并附带是否已授权给我的状态"""
#     return []


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
    requests = ApproveRequest.valid_objects.filter(user=request.user)
    if package:
        requests = requests.filter(action__extension__package=package)
    if is_approved == "true":
        requests = requests.exclude(status="wait")
    elif is_approved == "false":
        requests = requests.filter(status="wait")
    return requests


@api.get("/mine/switch_tenant/{id}/", response=MineSwitchTenantOut, tags=["我的"])
@operation(roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
def get_mine_switch_tenant(request, id):
    """租户切换"""
    tenant = Tenant.active_objects.get(id=id)

    return {
        "switch_tenant":{
            "id": tenant.id.hex,
            "slug": tenant.slug
        },
        "refresh": True
    }


@api.get("/tenant/{tenant_id}/mine/logout/", response=MineLogoutOut, tags=["我的"])
@operation(roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
def get_mine_logout(request, tenant_id: str):
    """退出登录"""
    request.auth.delete()
    return {"refresh": True}


@api.get("/mine/tenants/", response=List[MineTenantListItemOut], tags=["我的"])
@operation(roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(CustomPagination)
def get_mine_tenants(request):
    """获取我的租户"""
    tenants = Tenant.active_objects.filter(users=request.user).all()
    return list(tenants)


@api.get("/mine/tenant/{tenant_id}/mine_app_groups/", response=MineAppGroupListOut, tags=["我的"])
@operation(MineAppGroupListOut,roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
def get_mine_app_groups(request, tenant_id: str, parent_id=None):
    """获取我的应用分组
    """
    tenant = request.tenant
    appgroups = AppGroup.active_objects.filter(
        tenant=tenant
    )
    
    if parent_id in [0,"0",None,""]:
        # 传递虚拟节点则获取所有一级分组
        appgroups = list(appgroups.filter(parent=None).all())
    else:
        appgroups = list(appgroups.filter(parent__id=parent_id).all())
    
    return {"data": appgroups if appgroups else []}
    

@api.get("/mine/tenant/{tenant_id}/mine_group_apps/", response=List[MineAppListItemOut], tags=["我的"])
@operation(MineAppListOut,roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(CustomPagination)
def get_mine_apps_with_group(request, tenant_id: str, app_group_id=None):
    """获取我的分组应用
    """
    apps = []
    if app_group_id in [None,"","0",0]:
        apps = App.active_objects.filter(
            Q(tenant=request.tenant) | Q(entry_permission__is_open=True)
        )
    else:
        app_group = AppGroup.active_objects.get(
            tenant=request.tenant,
            id=app_group_id
        )
        
        apps = app_group.apps.filter(Q(tenant=request.tenant) | Q(entry_permission__is_open=True)).all()
        
    return list(apps) if apps else []

@api.get("/mine/unread_messages/",response=List(MineUnreadMessageListItemOut),tags=["我的"],auth=GlobalAuth())
@operation(MineUnreadMessageListOut,roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(CustomPagination)
def get_mine_unread_message(request):
    """我的未读消息列表
    """
    messages = Message.active_objects.filter(
        user = request.user,
        readed_status=False
    ).all()
    
    return list(messages)

@api.get("/mine/unread_messages/{id}/",response=MineUnreadMessageOut,tags=["我的"],auth=GlobalAuth())
@operation(MineUnreadMessageOut,roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
def get_mine_message(request):
    """ 获取我的消息
    """
    message= Message.active_objects.get(
        user=request.user,
        id=id
    )
    message.readed_status=True
    message.save()
    return message