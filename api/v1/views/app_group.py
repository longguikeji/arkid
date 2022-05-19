from typing import List
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
    if parent_id:
        groups = groups.filter(parent__id=parent_id)
    
    return {"data":list(groups.all())}


@api.get("/tenant/{tenant_id}/app_groups/{id}/", response=AppGroupOut, tags=["应用分组"],auth=None)
@operation(AppGroupOut)
def get_app_group(request, tenant_id: str, id: str):
    """ 获取应用分组
    """
    group = get_object_or_404(AppGroup,tenant_id=tenant_id,id=id)
    return {"data":group}

class AppGroupCreateIn(ModelSchema):
    class Config:
        model = AppGroup
        model_fields = ["name"]

class AppGroupCreateQueryIn(Schema):
    pass
        
class AppGroupCreateOut(Schema):
    pass

@api.post("/tenant/{tenant_id}/app_groups/", response=AppGroupCreateOut, tags=["应用分组"],auth=None)
@operation(AppGroupCreateOut)
def create_app_group(request, tenant_id: str, data: AppGroupCreateIn):
    """ 创建应用分组,TODO
    """
    group = AppGroup.active_objects.create(tenant=request.tenant,**data.dict())

    return {'error': ErrorCode.OK.value}


class AppGroupUpdateIn(ModelSchema):
    class Config:
        model = AppGroup
        model_fields = ["name"]

class AppGroupUpdateQueryIn(Schema):
    pass
        
class AppGroupUpdateOut(Schema):
    pass

@api.put("/tenant/{tenant_id}/app_groups/{id}/", response=AppGroupUpdateOut,tags=["应用分组"],auth=None)
@operation(AppGroupUpdateOut)
def update_app_group(request, tenant_id: str, id: str,data: AppGroupUpdateIn, query_data: AppGroupUpdateQueryIn=Query(...)):
    """ 编辑应用分组,TODO
    """
    return {}

class AppGroupDeleteQueryIn(Schema):
    pass
        
class AppGroupDeleteOut(Schema):
    pass

@api.delete("/tenant/{tenant_id}/app_groups/{id}/", response=AppGroupDeleteOut, tags=["应用分组"],auth=None)
@operation(AppGroupDeleteOut)
def delete_app_group(request, tenant_id: str, id: str,query_data: AppGroupDeleteQueryIn=Query(...)):
    """ 删除应用分组,TODO
    """
    return {}

@api.get("/tenant/{tenant_id}/app_groups/{app_group_id}/apps/",response=List[AppGroupAppItemOut],tags=["应用分组"],auth=None)
@operation(AppGroupAppsOut)
@paginate(CustomPagination)
def get_apps_from_group(request, tenant_id: str, app_group_id: str):
    """ 获取当前分组的应用列表,TODO
    """
    group = get_object_or_404(AppGroup,tenant_id=tenant_id,id=app_group_id)
    return group.apps.all()

class GroupAppRemoveQueryIn(Schema):
    pass
        
class GroupAppRemoveOut(Schema):
    pass

@api.delete("/tenant/{tenant_id}/app_groups/{app_group_id}/apps/{id}/",response=GroupAppRemoveOut, tags=["应用分组"],auth=None)
@operation(GroupAppRemoveOut)
def remove_app_from_group(request, tenant_id: str, app_group_id: str,id:str, query_data: GroupAppRemoveQueryIn=Query(...)):
    """ 将应用移除出应用分组,TODO
    """
    return {}

class GroupAppUpdateIn(Schema):
    pass

class GroupAppUpdateQueryIn(Schema):
    pass
        
class GroupAppUpdateOut(Schema):
    pass

@api.post("/tenant/{tenant_id}/app_groups/{app_group_id}/apps/", response=GroupAppUpdateOut,tags=["应用分组"],auth=None)
@operation(GroupAppUpdateOut)
def update_apps_from_group(request, tenant_id: str, app_group_id: str,data: GroupAppUpdateIn, query_data: GroupAppUpdateQueryIn=Query(...)):
    """ 更新当前分组的应用列表,TODO
    """
    return {}

class GroupAllAppQueryIn(Schema):
    pass
        
class GroupAllAppOut(Schema):
    pass

@api.get("/tenant/{tenant_id}/app_groups/{app_group_id}/select_apps/",response=List[GroupAllAppOut], tags=["应用分组"],auth=None)
@operation(List[GroupAllAppOut])
def get_select_apps(request, tenant_id: str, app_group_id: str, query_data: GroupAllAppQueryIn=Query(...)):
    """ 获取所有应用并附加是否在当前分组的状态,TODO
    """
    return {}


