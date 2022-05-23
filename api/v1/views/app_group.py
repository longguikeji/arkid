from typing import List
from django.apps import apps
from django.shortcuts import get_list_or_404, get_object_or_404
from ninja import Field, ModelSchema, Query, Schema
from requests import Response
from arkid.core.api import api,operation
from arkid.core.models import AppGroup
from arkid.core.translation import gettext_default as _
from api.v1.schema.app_group import *
from arkid.core.error import ErrorCode
from arkid.core.pagenation import CustomPagination
from ninja.pagination import paginate


@api.get("/tenant/{tenant_id}/app_groups/", response=AppGroupListOut,tags=["应用分组"],auth=None)
@operation(AppGroupListOut)
def get_app_groups(request, tenant_id: str, query_data: AppGroupListQueryIn=Query(...)):
    """ 应用分组列表
    """
    groups = AppGroup.active_objects.filter(tenant__id=tenant_id)
    
    parent_id = query_data.dict().get("parent_id",None)
    groups = groups.filter(parent__id=parent_id)
        
    
    return {"data":list(groups.all())}


@api.post("/tenant/{tenant_id}/app_groups/", response=AppGroupCreateOut, tags=["应用分组"],auth=None)
@operation(AppGroupCreateOut)
def create_app_group(request, tenant_id: str, data: AppGroupCreateIn):
    """ 创建应用分组,TODO
    """
    data = data.dict()
    if "parent" in data and data["parent"]:
        data["parent"] = get_object_or_404(AppGroup,id=data["parent"], is_del=False, is_active=True)
    group = AppGroup.active_objects.create(tenant=request.tenant,**data)

    return {'error': ErrorCode.OK.value}


@api.get("/tenant/{tenant_id}/app_groups/{id}/", response=AppGroupOut, tags=["应用分组"],auth=None)
@operation(AppGroupOut)
def get_app_group(request, tenant_id: str, id: str):
    """ 获取应用分组
    """
    group = get_object_or_404(AppGroup,tenant_id=tenant_id,id=id, is_del=False, is_active=True)
    return {
        "data": {
            "id": group.id.hex,
            "name": group.name,
            "parent": group.parent.id.hex if group.parent else ""
        }
    }

@api.post("/tenant/{tenant_id}/app_groups/{id}/", response=AppGroupUpdateOut,tags=["应用分组"],auth=None)
@operation(AppGroupUpdateOut)
def update_app_group(request, tenant_id: str, id: str,data: AppGroupUpdateIn):
    """ 编辑应用分组,TODO
    """
    group = get_object_or_404(AppGroup,tenant_id=tenant_id,id=id, is_del=False, is_active=True)
    for attr, value in data.dict().items():
        setattr(group, attr, value)
    group.save()
    return {'error': ErrorCode.OK.value}

@api.delete("/tenant/{tenant_id}/app_groups/{id}/", response=AppGroupDeleteOut, tags=["应用分组"],auth=None)
@operation(AppGroupDeleteOut)
def delete_app_group(request, tenant_id: str, id: str):
    """ 删除应用分组,TODO
    """
    group = get_object_or_404(AppGroup,id=id, is_del=False, is_active=True)
    group.delete()
    return {'error': ErrorCode.OK.value}

@api.get("/tenant/{tenant_id}/app_groups/{app_group_id}/apps/",response=List[AppGroupAppListItemOut],tags=["应用分组"],auth=None)
@operation(AppGroupAppListOut)
@paginate(CustomPagination)
def get_apps_from_group(request, tenant_id: str, app_group_id: str):
    """ 获取当前分组的应用列表,TODO
    """
    group = get_object_or_404(AppGroup,tenant_id=tenant_id,id=app_group_id, is_del=False, is_active=True)
    return group.apps.all()


@api.delete("/tenant/{tenant_id}/app_groups/{app_group_id}/apps/{id}/",response=AppGroupAppRemoveOut, tags=["应用分组"],auth=None)
@operation(AppGroupAppRemoveOut)
def remove_app_from_group(request, tenant_id: str, app_group_id: str,id:str):
    """ 将应用移除出应用分组,TODO
    """
    
    app = get_object_or_404(App,tenant__id=tenant_id, id=id, is_del=False, is_active=True)
    group = get_object_or_404(AppGroup,tenant__id=tenant_id, id=app_group_id, is_del=False, is_active=True)
    group.apps.remove(app)
    group.save()
    return {'error': ErrorCode.OK.value}

@api.post("/tenant/{tenant_id}/app_groups/{app_group_id}/apps/", response=AppGroupAppUpdateOut,tags=["应用分组"],auth=None)
@operation(AppGroupAppUpdateOut)
def update_apps_from_group(request, tenant_id: str, app_group_id: str,data: AppGroupAppUpdateIn):
    """ 更新当前分组的应用列表,TODO
    """
    group = get_object_or_404(AppGroup,tenant__id=tenant_id, id=app_group_id, is_del=False, is_active=True)
    app_ids = data.dict()["apps"]
    apps = App.active_objects.filter(tenant__id=tenant_id,id__in=app_ids, is_del=False, is_active=True).all()
    
    for app in apps:
        group.apps.add(app)
    
    group.save()
    
    return {'error': ErrorCode.OK.value}


@api.get("/tenant/{tenant_id}/app_groups/{app_group_id}/select_apps/",response=List[AppGroupSelectAppsItemOut], tags=["应用分组"],auth=None)
@operation(AppGroupSelectAppsOut)
@paginate(CustomPagination)
def get_select_apps(request, tenant_id: str, app_group_id: str):
    """ 获取所有应用并附加是否在当前分组的状态,TODO
    """
    
    group = get_object_or_404(AppGroup,id=app_group_id, is_del=False, is_active=True)
    selected_apps = group.apps.filter(is_del=False, is_active=True).all()
    apps = App.active_objects.filter(tenant__id=tenant_id).all()
    
    return [
        {
            "id": item.id,
            "name": item.name,
            "status": True if item in selected_apps else False
        }
        for item in apps
    ]


