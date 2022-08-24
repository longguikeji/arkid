from typing import List
from django.urls import reverse
from django.shortcuts import render
from arkid.config import get_app_config
from arkid.core.api import api, operation
from arkid.core.error import ErrorCode, ErrorDict, SuccessDict
from arkid.core.translation import gettext_default as _
from arkid.core.pagenation import CustomPagination
from arkid.core.models import App, Tenant, ApproveRequest, User
from arkid.core.constants import NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN
from django.http import HttpResponseRedirect
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


@api.get("/mine/tenant/{tenant_id}/accounts/", tags=["我的"], response=List[MineBindAccountItem])
@operation(MineBindAccountOut,roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(CustomPagination)
def get_mine_accounts(request, tenant_id: str, show_type:str = 'bind'):
    """我的绑定账号"""
    from arkid.core.expand import field_expand_map
    from arkid.extension.models import Extension as ExtensionModel
    user_expand = request.user_expand
    # 梳理出登录类型的插件
    qs = ExtensionModel.valid_objects.all()
    qs_dict = {}
    for item in qs:
        if item.type == 'external_idp':
            qs_dict[str(item.package).replace('.','_')] = item
    # 筛选出用户所拥有的插件
    table_name = User._meta.db_table
    items = []
    if table_name in field_expand_map:
        field_expands = field_expand_map.get(table_name,{})
        for table, field,extension_name,extension_model_cls,extension_table,extension_field  in field_expands:
            for field_item in extension_model_cls._meta.fields:
                verbose_name = field_item.verbose_name
                field_name = field_item.name
                if field_name == field:
                    if extension_name in qs_dict and field_name in user_expand:
                        user_filter_value = user_expand.get(field_name, None)
                        if user_filter_value and show_type == 'bind':
                            qs_item = qs_dict.get(extension_name)
                            items.append({
                                'id': qs_item.id,
                                'name': qs_item.name
                            })
                        elif (user_filter_value is None or user_filter_value == '') and show_type == 'unbind':
                            qs_item = qs_dict.get(extension_name)
                            items.append({
                                'id': qs_item.id,
                                'name': qs_item.name
                            })
                        break
    return items


@api.get("/mine/tenant/{tenant_id}/accounts/{account_id}/unbind", tags=["我的"])
@operation(roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
def unbind_mine_account(request, tenant_id: str, account_id: str):
    '''
    解绑我的账号
    '''
    from arkid.core.expand import field_expand_map
    from arkid.extension.models import Extension as ExtensionModel
    user_expand = request.user_expand
    user = request.user
    # 梳理出登录类型的插件
    qs = ExtensionModel.valid_objects.all()
    qs_dict = {}
    select_package = None
    for item in qs:
        if item.type == 'external_idp' and str(item.id) == account_id:
            select_package = str(item.package).replace('.','_')
            break

    if select_package:
        table_name = User._meta.db_table
        items = []
        if table_name in field_expand_map:
            field_expands = field_expand_map.get(table_name,{})
            for table, field,extension_name,extension_model_cls,extension_table,extension_field  in field_expands:
                for field_item in extension_model_cls._meta.fields:
                    verbose_name = field_item.verbose_name
                    field_name = field_item.name
                    if field_name == field and extension_name == select_package:
                        extension_model_cls.valid_objects.filter(
                            target=user
                        ).delete()
                        break
    return ErrorDict(ErrorCode.OK) 



@api.get("/mine/tenant/{tenant_id}/accounts/{account_id}/bind", tags=["我的"])
@operation(roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
def bind_mine_account(request, tenant_id: str, account_id: str):
    '''
    绑定我的账户
    '''
    from arkid.extension.models import TenantExtensionConfig, Extension as ExtensionModel
    server_host = get_app_config().get_host()
    front_host = get_app_config().get_frontend_host()
    # 梳理出登录类型的插件
    qs = ExtensionModel.valid_objects.all()
    select_package = None
    for item in qs:
        if item.type == 'external_idp' and str(item.id) == account_id:
            select_package = str(item.package).replace('.','_')
            break
    # 取得租户的插件配置
    config_created = TenantExtensionConfig.valid_objects.filter(tenant_id=tenant_id, extension_id=account_id).order_by('-created').first()
    if config_created and select_package:
        login_url = server_host + reverse(
            f'api:{select_package}:{select_package}_login',
            args=[config_created.id],
        )
        login_url = login_url + '?next={}/mine_auth_manage'.format(front_host)
        return HttpResponseRedirect(login_url)
    return ErrorCode(ErrorCode.OK)