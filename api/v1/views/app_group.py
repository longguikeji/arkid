from typing import List
from ninja import Field, ModelSchema, Query, Schema
from requests import Response
from arkid.core.api import api,operation
from arkid.core.models import AppGroup
from arkid.core.translation import gettext_default as _


class AppGroupListQueryIn(Schema):
    pass
        
class AppGroupListOut(ModelSchema):
    class Config:
        model = AppGroup
        model_fields = ["name"]

@api.get("/tenant/{tenant_id}/app_groups/", response=List[AppGroupListOut],tags=["应用分组"],auth=None)
@operation(List[AppGroupListOut])
def get_app_groups(request, tenant_id: str, query_data: AppGroupListQueryIn=Query(...)):
    """ 应用分组列表,TODO
    """
    groups = AppGroup.expand_objects.filter(tenant__id=tenant_id).all()
    return groups

class AppGroupQueryIn(Schema):
    pass
        
class AppGroupOut(ModelSchema):
    class Config:
        model = AppGroup
        model_fields = ["name"]

@api.get("/tenant/{tenant_id}/app_groups/{id}/", response=AppGroupOut, tags=["应用分组"],auth=None)
@operation(AppGroupOut)
def get_app_group(request, tenant_id: str, id: str, query_data: AppGroupQueryIn=Query(...)):
    """ 获取应用分组,TODO
    """
    return {}

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
def create_app_group(request, tenant_id: str, data: AppGroupCreateIn, query_data: AppGroupCreateQueryIn=Query(...)):
    """ 创建应用分组,TODO
    """
    group = AppGroup.expand_objects.create(**data)

    return {}


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

class GroupAppsQueryIn(Schema):
    pass
        
class GroupAppsOut(Schema):
    pass

@api.get("/tenant/{tenant_id}/app_groups/{app_group_id}/apps/",response=List[GroupAppsOut],tags=["应用分组"],auth=None)
@operation(List[GroupAppsOut])
def get_apps_from_group(request, tenant_id: str, app_group_id: str, query_data: GroupAppsQueryIn=Query(...)):
    """ 获取当前分组的应用列表,TODO
    """
    return []

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


