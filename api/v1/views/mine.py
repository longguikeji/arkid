from typing import List
from ninja import Query
from django.urls import reverse
from django.shortcuts import render
from arkid.common.utils import deep_merge
from arkid.config import get_app_config
from arkid.core.api import GlobalAuth, api, operation
from arkid.core.error import ErrorCode, ErrorDict, SuccessDict
from arkid.core.translation import gettext_default as _
from arkid.core.pagenation import CustomPagination
from arkid.core.event import ACCOUNT_UNBIND, dispatch_event, Event
from arkid.core.models import App, AppGroup, Message, Tenant, ApproveRequest, User, UserPersonalSettings
from arkid.core.constants import *
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
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
    query_data:MinePermissionListQueryIn=Query(...)
):
    """我的权限列表"""
    login_user = request.user
    from arkid.core.perm.permission_data import PermissionData

    permissiondata = PermissionData()
    items = permissiondata.get_permissions_by_mine_search(
        tenant_id, query_data.app_id, None, None, login_user, app_name=query_data.app_name, category=query_data.category, operation_id=query_data.operation_id, name=query_data.name,
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
    requests = ApproveRequest.valid_objects.filter(user=request.user, tenant=tenant)
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
@operation(roles=[PLATFORM_USER, PLATFORM_ADMIN])
@paginate(CustomPagination)
def get_mine_tenants(request):
    """获取我的租户"""
    tenants = list(Tenant.active_objects.filter(users=request.user).all())
    for tenant in tenants:
        if tenant.has_admin_perm(request.user):
            tenant.role = '管理员'
        else:
            tenant.role = '普通用户'
    return tenants


@api.get("/mine/tenants/all/", response=MineTenantAllOut, tags=["我的"])
@operation(roles=[PLATFORM_USER, PLATFORM_ADMIN])
def get_mine_tenants_all(request):
    """获取我的租户"""
    tenants = list(Tenant.active_objects.filter(users=request.user).all())
    for tenant in tenants:
        if tenant.has_admin_perm(request.user):
            tenant.role = '管理员'
        else:
            tenant.role = '普通用户'
    return SuccessDict(data=tenants)

@api.get("/mine/tenant/{tenant_id}/accounts/", tags=["我的"], response=List[MineBindAccountItem])
@operation(MineBindAccountOut,roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(CustomPagination)
def get_mine_accounts(request, tenant_id: str):
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
    add_package_record = []
    items = []
    if table_name in field_expand_map:
        field_expands = field_expand_map.get(table_name,{})
        for table, field,extension_name,extension_model_cls,extension_table,extension_field  in field_expands:
            for field_item in extension_model_cls._meta.fields:
                verbose_name = field_item.verbose_name
                field_name = field_item.name
                if field_name == field:
                    if extension_name in qs_dict and field_name in user_expand and extension_name not in add_package_record:
                        user_filter_value = user_expand.get(field_name, None)
                        if user_filter_value:
                            qs_item = qs_dict.get(extension_name)
                            first_field_name = field_name.replace("user_id", "")
                            nickname_field_name = first_field_name+'nickname'
                            avatar_field_name = first_field_name+'avatar'
                            items.append({
                                'id': qs_item.id,
                                'name': qs_item.name,
                                'nickname': user_expand.get(nickname_field_name, ''),
                                'avatar': user_expand.get(avatar_field_name, '')
                                # 'nickname': qs_item.nickname,
                                # 'avatar': qs_item.avatar
                            })
                            add_package_record.append(extension_name)
                        break
    return items


@api.get("/mine/tenant/{tenant_id}/unbind_accounts/", tags=["我的"], response=List[MineUnBindAccountItem])
@operation(MineUnBindAccountOut,roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(CustomPagination)
def get_mine_unbind_accounts(request, tenant_id: str):
    """我的没绑定账户"""
    from arkid.core.expand import field_expand_map
    from arkid.extension.models import Extension as ExtensionModel
    user_expand = request.user_expand
    # 梳理出登录类型的插件
    qs = ExtensionModel.valid_objects.all()
    qs_dict = {}
    exclude_packages = ['com.longgui.external.idp.miniprogram']
    for item in qs:
        if item.type == 'external_idp' and item.package not in exclude_packages:
            qs_dict[str(item.package).replace('.','_')] = item
    # 筛选出用户所拥有的插件
    table_name = User._meta.db_table
    items = []
    add_package_record = []
    if table_name in field_expand_map:
        field_expands = field_expand_map.get(table_name,{})
        for table, field,extension_name,extension_model_cls,extension_table,extension_field  in field_expands:
            for field_item in extension_model_cls._meta.fields:
                verbose_name = field_item.verbose_name
                field_name = field_item.name
                if field_name == field:
                    if extension_name in qs_dict and field_name in user_expand and extension_name not in add_package_record:

                        user_filter_value = user_expand.get(field_name, None)
                        if 'id' in field_name and (user_filter_value is None or user_filter_value == ''):
                            qs_item = qs_dict.get(extension_name)
                            items.append({
                                'id': qs_item.id,
                                'name': qs_item.name
                            })
                            add_package_record.append(extension_name)
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
                        # 发送取消绑定事件
                        select_package = select_package.replace('_','.')
                        data = {
                            'user_id': str(request.user.id)
                        }
                        dispatch_event(Event(tag=ACCOUNT_UNBIND, tenant=request.tenant, request=request, data=data, packages=[select_package]))
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
        login_url = login_url + '?next={}/mine/mine_auth_manage'.format(front_host)
        return {
            "redirect":login_url
        }
    else:
        return ErrorDict(ErrorCode.PLUG_IN_NOT_START)

@api.get("/mine/tenant/{tenant_id}/mine_app_groups/", response=MineAppGroupListOut, tags=["我的"])
@operation(MineAppGroupListOut,roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
def get_mine_app_groups(request, tenant_id: str, parent_id=None):
    """获取我的应用分组
    """
    tenant = request.tenant
    appgroups = AppGroup.active_objects.filter(
        tenant=tenant
    )
    if parent_id in [None,""]:
        # 未传则获取所有一级分组
        appgroups = appgroups.filter(parent=None)
    elif parent_id in [0,"0"]:
        # 虚拟节点返回空
        appgroups = []
    else:
        appgroups = appgroups.filter(parent__id=parent_id)
    # 需要排除掉空分组数据
    ids = []
    for appgroup in appgroups:
        if appgroup.apps.exists():
            ids.append(appgroup.id)
    if ids:
        appgroups = appgroups.filter(id__in=ids).all()
    else:
        appgroups = []
    return {"data": list(appgroups) if appgroups else []}
    

@api.get("/mine/tenant/{tenant_id}/mine_group_apps/", response=List[MineAppListItemOut], tags=["我的"])
@operation(MineAppListOut,roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(CustomPagination)
def get_mine_apps_with_group(request, tenant_id: str, query_data:MineAppsGroupQueryIn=Query(...)):
    """获取我的分组应用
    """
    app_group_id = query_data.app_group_id
    order = query_data.order
    name = query_data.name

    apps = []
    if app_group_id in [None,"","0",0]:
        apps = App.active_objects.filter(
            Q(tenant=request.tenant) | Q(entry_permission__is_open=True)
        )
    else:
        app_group = AppGroup.active_objects.get(
            tenant =request.tenant,
            id=app_group_id
        )
        apps = app_group.apps.filter(Q(tenant=request.tenant) | Q(entry_permission__is_open=True))
    # 需要甄别有入口权限的应用
    from arkid.core.perm.permission_data import PermissionData
    pd = PermissionData()
    app_ids = pd.get_entry_apps(request.user, tenant_id, apps)
    if app_ids:
        apps = apps.filter(id__in=app_ids)
    else:
        apps = apps.filter(id=None)
    if name:
        name = name.strip()
        apps = apps.filter(name__icontains=name)
    if order:
        apps = apps.order_by(order)
    apps = apps.all()
        
    return list(apps) if apps else []

@api.get("/mine/tenant/{tenant_id}/mine_group_apps_all/", response=MineAppListOut, tags=["我的"])
@operation(MineAppListOut,roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
def get_mine_apps_with_group_all(request, tenant_id: str, app_group_id:str=None, order:str=None):
    """获取我的分组应用
    """
    apps = []
    if app_group_id in [None,"","0",0]:
        apps = App.active_objects.filter(
            Q(tenant=request.tenant) | Q(entry_permission__is_open=True)
        )
    else:
        app_group = AppGroup.active_objects.get(
            tenant =request.tenant,
            id=app_group_id
        )
        apps = app_group.apps.filter(Q(tenant=request.tenant) | Q(entry_permission__is_open=True))
    # 需要甄别有入口权限的应用
    from arkid.core.perm.permission_data import PermissionData
    pd = PermissionData()
    app_ids = pd.get_entry_apps(request.user, tenant_id, apps)
    if app_ids:
        apps = apps.filter(id__in=app_ids)
    else:
        apps = apps.filter(id=None)
    if order:
        apps = apps.order_by(order)
    apps = apps.all()
        
    return SuccessDict(data=list(apps) if apps else [])

@api.get("/mine/unread_messages/",response=List[MineMessageListItemOut],tags=["我的"],auth=GlobalAuth())
@operation(MineMessageListOut,roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(CustomPagination)
def get_mine_unread_message(request):
    """我的未读消息列表
    """
    messages = Message.active_objects.filter(
        user = request.user,
        readed_status=False
    ).all()
    
    return list(messages)

@api.get("/mine/unread_messages/{id}/",response=MineMessageOut,tags=["我的"],auth=GlobalAuth())
@operation(MineMessageOut,roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
def get_mine_message(request, id:str):
    """ 获取我的消息
    """
    message= Message.active_objects.get(
        user=request.user,
        id=id
    )
    message.readed_status=True
    message.save()
    return SuccessDict(data=message)

@api.get("/mine/message_senders/",response=MessageSenderOut,tags=["我的"],auth=GlobalAuth())
@operation(MessageSenderOut,roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
def get_mine_message_senders(request):
    messages = Message.active_objects.filter(
        user = request.user,
    ).all()
    senders = list(set([ item.sender for item in messages ]))
    return SuccessDict(data=[
        {
            "id": sender.id.hex if sender else 0,
            "name": sender.username if sender else _("系统消息"),
            "avatar": sender.avatar if sender and sender.avatar else ""
        }
        for sender in senders
    ])


@api.get("/mine/sender_messages/{id}/",response=List[MineMessageListItemOut],tags=["我的"],auth=GlobalAuth())
@operation(MineMessageListOut,roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(CustomPagination)
def get_mine_sender_messages(request,id:str):
    """我的消息
    """
    messages = Message.active_objects.filter(
        user = request.user,
    )
    if not id in [0,"0",None]:
        messages = messages.filter(Q(sender__id=id,user=request.user)|Q(user__id=id,sender=request.user))
    else:
        messages = messages.filter(Q(sender=None,user=request.user))
    messages = messages.order_by('-created').all()
    
    return list(messages)

@api.get("/mine/unreaded_message_count/",response=MineUnreadedMessageCountOut,tags=["我的"],auth=GlobalAuth())
@operation(MineUnreadedMessageCountOut,roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
def get_unreaded_message_count(request):
    return SuccessDict(
        data={
            "count":Message.active_objects.filter(user=request.user,readed_status=False).count()
        }
    )
    
@api.get("/mine/tenant/{tenant_id}/personal_settings/",response=MinePersonalSettingsOut,tags=["我的"],auth=GlobalAuth())
@operation(MinePersonalSettingsOut,roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
def get_personal_settings(request,tenant_id:str):
    """获取个人设置信息
    """
    setting, _ = UserPersonalSettings.active_objects.get_or_create(
        tenant=request.tenant,
        user=request.user
    )
    
    if not setting.settings:
        setting.settings = {
            "desktop":{
                
            }
        }
        setting.save()
    
    return SuccessDict(
        data=setting.settings
    )
    
@api.post("/mine/tenant/{tenant_id}/personal_settings/",response=MinePersonalSettingsOut,tags=["我的"],auth=GlobalAuth())
@operation(MinePersonalSettingsOut,roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
def post_personal_settings(request,tenant_id:str,data:MinePersonalSettingsIn):
    """获取个人设置信息
    """
    setting, _ = UserPersonalSettings.active_objects.get_or_create(
        tenant=request.tenant,
        user=request.user
    )
    
    setting.settings = deep_merge(setting.settings,data.dict())
    setting.save()
    
    return SuccessDict(
        data=setting.settings
    )