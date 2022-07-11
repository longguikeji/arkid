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
from api.v1.schema.user import (
    UserCreateIn, UserCreateOut, UserDeleteOut,
    UserListItemOut, UserListOut, UserListQueryIn,
    UserOut, UserUpdateIn, UserUpdateOut,
    UserFieldsOut,
)
from arkid.core.error import ErrorCode, ErrorDict
from arkid.core.constants import NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN
from arkid.core.pagenation import CustomPagination
from ninja.pagination import paginate

# ------------- 用户列表接口 --------------        
@api.get("/tenant/{tenant_id}/users/",response=List[UserListItemOut], tags=['用户'])
@operation(UserListOut)
@paginate(CustomPagination)
def user_list(request, tenant_id: str, query_data: UserListQueryIn=Query(...)):
    from arkid.core.perm.permission_data import PermissionData
    users = User.expand_objects.filter(tenant_id=tenant_id, is_del=False,is_active=True)
    login_user = request.user
    tenant = request.tenant
    pd = PermissionData()
    users = pd.get_manage_all_user(login_user, tenant, users)
    return list(users)

@api.get("/tenant/{tenant_id}/user_no_super/",response=UserListOut, tags=['用户'])
@operation(UserListOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
# @paginate(CustomPagination)
def user_list(request, tenant_id: str):
    from arkid.core.perm.permission_data import PermissionData
    super_user_id = User.valid_objects.order_by('created').first().id
    users = User.valid_objects.filter(tenant_id=tenant_id).exclude(id=super_user_id)
    # 如果当前登录的用户不是管理员，需要根据用户所拥有的分组进行区分
    login_user = request.user
    tenant = request.tenant
    pd = PermissionData()
    users = pd.get_manage_all_user(login_user, tenant, users)
    return {"data": list(users.all())}

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

# ------------- 用户扩展字段列表 --------------
@api.get("/tenant/{tenant_id}/user_fields/", response=UserFieldsOut, tags=['用户'], auth=None)
def user_fields(request, tenant_id: str):
    from arkid.core.expand import field_expand_map
    table_name = User._meta.db_table
    items = []
    if table_name in field_expand_map:
        field_expands = field_expand_map.get(table_name,{})
        for table, field,extension_name,extension_model_cls,extension_table,extension_field  in field_expands:
            for field_item in extension_model_cls._meta.fields:
                verbose_name = field_item.verbose_name
                field_name = field_item.name
                if field_name == field:
                    items.append({
                        'id': field,
                        'name': verbose_name,
                    })
                    break
    return {"data":items}
# ------------- 获取用户接口 --------------
        
@api.get("/tenant/{tenant_id}/users/{id}/",response=UserOut, tags=['用户'], auth=None)
@operation(UserOut)
def get_user(request, tenant_id: str,id:str):
    id = id.replace("-", "")
    user = User.expand_objects.get(id=id)
    return {"data":user}
