from email import message
from typing import Any, Dict, Optional, List
from django.shortcuts import get_object_or_404
from pydantic import Field
from ninja import Schema, Query, ModelSchema
from arkid.core.event import Event, register_event, dispatch_event
from arkid.core.api import api, operation
from arkid.core.models import Tenant, User
from arkid.core.translation import gettext_default as _
from arkid.core.event import CREATE_LOGIN_PAGE_AUTH_FACTOR, CREATE_LOGIN_PAGE_RULES
from arkid.common.logger import logger
from api.v1.schema.user import UserCreateIn, UserCreateOut, UserDeleteOut, UserListItemOut, UserListOut, UserListQueryIn, UserOut, UserUpdateIn, UserUpdateOut
from arkid.core.error import ErrorCode, ErrorDict
from arkid.core.pagenation import CustomPagination
from ninja.pagination import paginate

# ------------- 用户列表接口 --------------        
@api.get("/tenant/{tenant_id}/users/",response=List[UserListItemOut], tags=['用户'], auth=None)
@operation(UserListOut)
@paginate(CustomPagination)
def user_list(request, tenant_id: str, query_data: UserListQueryIn=Query(...)):
    users = User.expand_objects.filter(is_del=False,is_active=True)
    return list(users)

# ------------- 创建用户接口 --------------
@api.post("/tenant/{tenant_id}/users/",response=UserCreateOut, tags=['用户'], auth=None)
@operation(UserCreateOut)
def user_create(request, tenant_id: str,data:UserCreateIn):

    # user = User.expand_objects.create(tenant=request.tenant,**data.dict())
    user = User.objects.create(tenant=request.tenant, username=data.username)
    for key,value in data.dict().items():
        if key=='username':
            continue
        setattr(user,key,value)
    user.save()

    return {"data":{"user":user.id.hex}}

# ------------- 删除用户接口 --------------    
@api.delete("/tenant/{tenant_id}/users/{id}/",response=UserDeleteOut, tags=['用户'], auth=None)
@operation(UserDeleteOut)
def user_delete(request, tenant_id: str,id:str):
    user = get_object_or_404(User,tenant=request.tenant, id=id)
    user.delete()
    return {"error":ErrorCode.OK.value}
        
# ------------- 更新用户接口 --------------
@api.post("/tenant/{tenant_id}/users/{id}/",response=UserUpdateOut, tags=['用户'], auth=None)
@operation(UserUpdateOut)
def user_update(request, tenant_id: str,id:str, data:UserUpdateIn):

    user = User.objects.get(id=id)
    for key,value in data.dict().items():
        setattr(user,key,value)
    user.save()
    return {"error":ErrorCode.OK.value}
# ------------- 获取用户接口 --------------
        
@api.get("/tenant/{tenant_id}/users/{id}/",response=UserOut, tags=['用户'], auth=None)
@operation(UserOut)
def get_user(request, tenant_id: str,id:str):
    id = id.replace("-", "")
    user = User.expand_objects.get(id=id)
    return {"data":user}


@api.get("/tenant/{tenant_id}/users/{user_id}/permissions/",tags=["用户"],auth=None)
def get_user_permissions(request, tenant_id: str,user_id:str):
    """ 用户权限列表,TODO
    """
    return []

@api.post("/tenant/{tenant_id}/users/{user_id}/permissions/",tags=["用户"],auth=None)
def update_user_permissions(request, tenant_id: str,user_id:str):
    """ 更新用户权限列表,TODO
    """
    return []

@api.delete("/tenant/{tenant_id}/users/{user_id}/permissions/{id}/",tags=["用户"],auth=None)
def delete_user_permissions(request, tenant_id: str,user_id:str,id:str):
    """ 删除用户权限,TODO
    """
    return []

@api.get("/tenant/{tenant_id}/users/{user_id}/all_permissions/",tags=["用户"],auth=None)
def get_user_all_permissions(request, tenant_id: str,user_id:str):
    """ 获取所有权限并附带是否已授权给用户状态,TODO
    """
    return []