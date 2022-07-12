from typing import List
from django.apps import apps
from django.shortcuts import get_list_or_404, get_object_or_404
from ninja import Field, ModelSchema, Query, Schema
from requests import Response
from arkid.core.api import api,operation
from arkid.core.constants import *
from arkid.core.models import AppGroup
from arkid.core.error import ErrorCode, ErrorDict
from arkid.core.translation import gettext_default as _
from api.v1.schema.app_group import *
from arkid.core.error import ErrorCode, ErrorDict
from arkid.core.pagenation import CustomPagination
from ninja.pagination import paginate


@api.get("/tenant/{tenant_id}/app_groups/", response=AppGroupListOut,tags=["应用分组"])
@operation(AppGroupListOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def get_app_groups(request, tenant_id: str, query_data: AppGroupListQueryIn=Query(...)):
    """ 应用分组列表
    """
    groups = AppGroup.expand_objects.filter(tenant__id=tenant_id)
    
    parent_id = query_data.dict().get("parent_id",None)
    groups = groups.filter(parent__id=parent_id)
        
    
    return {"data":list(groups.all())}


@api.post("/tenant/{tenant_id}/app_groups/", response=AppGroupCreateOut, tags=["应用分组"])
@operation(AppGroupCreateOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def create_app_group(request, tenant_id: str, data: AppGroupCreateIn):
    """ 创建应用分组
    """
    data = data.dict()
    if "parent" in data and data["parent"]:
        data["parent"] = get_object_or_404(AppGroup.active_objects,id=data["parent"].get("id"), is_del=False, is_active=True)
    group = AppGroup.expand_objects.create(tenant=request.tenant,**data)

    return ErrorDict(ErrorCode.OK)


@api.get("/tenant/{tenant_id}/app_groups/{id}/", response=AppGroupOut, tags=["应用分组"])
@operation(AppGroupOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def get_app_group(request, tenant_id: str, id: str):
    """ 获取应用分组
    """
    group = get_object_or_404(AppGroup.expand_objects,tenant_id=tenant_id,id=id, is_del=False, is_active=True)
    group["parent"] = AppGroup.active_objects.get(id=group["parent_id"]) if group["parent_id"] else None
    return {
        "data": group
    }

@api.post("/tenant/{tenant_id}/app_groups/{id}/", response=AppGroupUpdateOut,tags=["应用分组"])
@operation(AppGroupUpdateOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def update_app_group(request, tenant_id: str, id: str,data: AppGroupUpdateIn):
    """ 编辑应用分组
    """
    group = get_object_or_404(AppGroup.active_objects, id=id)
    parent = data.dict().get("parent",None)
    parent_id = parent.get("id",None) if parent else None
    group.parent = get_object_or_404(AppGroup.active_objects, id=parent_id) if parent_id else None
    if group.parent == group:
        return ErrorDict(ErrorCode.APP_GROUP_PARENT_CANT_BE_ITSELF)
    group.name = data.dict().get("name",group.name)
    group.save()
    return ErrorDict(ErrorCode.OK)

@api.delete("/tenant/{tenant_id}/app_groups/{id}/", response=AppGroupDeleteOut, tags=["应用分组"])
@operation(AppGroupDeleteOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def delete_app_group(request, tenant_id: str, id: str):
    """ 删除应用分组
    """
    group = get_object_or_404(AppGroup.expand_objects,id=id, is_del=False, is_active=True)
    group.delete()
    return ErrorDict(ErrorCode.OK)

@api.get("/tenant/{tenant_id}/app_groups/{app_group_id}/apps/",response=List[AppGroupAppListItemOut],tags=["应用分组"])
@operation(AppGroupAppListOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(CustomPagination)
def get_apps_from_group(request, tenant_id: str, app_group_id: str):
    """ 获取当前分组的应用列表
    """
    group = get_object_or_404(AppGroup,tenant_id=tenant_id,id=app_group_id, is_del=False, is_active=True)
    return group.apps.all()


@api.delete("/tenant/{tenant_id}/app_groups/{app_group_id}/apps/{id}/",response=AppGroupAppRemoveOut, tags=["应用分组"])
@operation(AppGroupAppRemoveOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def remove_app_from_group(request, tenant_id: str, app_group_id: str,id:str):
    """ 将应用移除出应用分组
    """
    
    app = get_object_or_404(App,tenant__id=tenant_id, id=id, is_del=False, is_active=True)
    group = get_object_or_404(AppGroup,tenant__id=tenant_id, id=app_group_id, is_del=False, is_active=True)
    group.apps.remove(app)
    group.save()
    return ErrorDict(ErrorCode.OK)

@api.post("/tenant/{tenant_id}/app_groups/{app_group_id}/apps/", response=AppGroupAppUpdateOut,tags=["应用分组"])
@operation(AppGroupAppUpdateOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def update_apps_from_group(request, tenant_id: str, app_group_id: str,data: AppGroupAppUpdateIn):
    """ 更新当前分组的应用列表
    """
    group = get_object_or_404(AppGroup,tenant__id=tenant_id, id=app_group_id, is_del=False, is_active=True)
    app_ids = data.dict()["apps"]
    apps = App.active_objects.filter(tenant__id=tenant_id,id__in=app_ids, is_del=False, is_active=True).all()
    
    for app in apps:
        group.apps.add(app)
    
    group.save()
    
    return ErrorDict(ErrorCode.OK)


@api.get("/tenant/{tenant_id}/app_groups/{app_group_id}/exclude_apps/",response=List[AppGroupExcludeAppsItemOut], tags=["应用分组"])
@operation(AppGroupExcludeAppsOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(CustomPagination)
def get_exclude_apps(request, tenant_id: str, app_group_id: str):
    """ 获取所有未添加到分组的应用
    """
    
    group = get_object_or_404(AppGroup,id=app_group_id,tenant=request.tenant, is_del=False, is_active=True)
    selected_apps = group.apps.filter(is_del=False, is_active=True).all()
    apps = App.expand_objects.filter(tenant__id=tenant_id).exclude(id__in=selected_apps).all()
    
    return apps


