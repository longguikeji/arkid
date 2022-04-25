from email import message
from typing import Any, Dict, Optional, List
from pydantic import Field
from ninja import Schema, Query, ModelSchema
from arkid.core.event import Event, register_event, dispatch_event
from arkid.core.api import api, operation
from arkid.core.models import Tenant, User
from arkid.core.translation import gettext_default as _
from arkid.core.event import CREATE_LOGIN_PAGE_AUTH_FACTOR, CREATE_LOGIN_PAGE_RULES
from arkid.common.logger import logger

# ------------- 用户列表接口 --------------

class UserListInSchema(Schema):
    pass

class UserListOutSchema(ModelSchema):
     class Config:
        model = User
        model_fields = ['id', 'username', 'avatar', 'is_platform_user']
        
@api.get("/tenant/{tenant_id}/users/",response=List[UserListOutSchema], tags=['用户'], auth=None)
@operation(List[UserListOutSchema])
def user_list(request, tenant_id: str,data: UserListInSchema=Query(...)):
    users = User.expand_objects.filter(tenant__id=tenant_id).all()
    return users

# ------------- 创建用户接口 --------------

class UserCreateInQuerySchema(Schema):
    pass

class UserCreateInSchema(ModelSchema):
    class Config:
        model = User
        model_fields = ['username', 'avatar', 'is_platform_user']
        
class UserCreateOutSchema(Schema):
    status:bool = Field(
        title=_("状态")
    )
    
    message:str = Field(
        title=_("状态说明")
    )
        
@api.post("/tenant/{tenant_id}/users/",response=UserCreateOutSchema, tags=['用户'], auth=None)
@operation(UserCreateOutSchema)
def user_create(request, tenant_id: str,data:UserCreateInSchema, query_data: UserCreateInQuerySchema=Query(...)):
    status = True,
    message = ""
    try:
        users = User.expand_objects.create(tenant__id=tenant_id,**data.dict())
    except Exception as e:
        status = False
        message= f'{_("创建用户失败")}:{str(e)}'
        logger.error(message)

    return {
        "status": status,
        "message": message
    }
# ------------- 删除用户接口 --------------

class UserDeleteInSchema(Schema):
    pass
        
class UserDeleteOutSchema(Schema):
    status:bool = Field(
        title=_("状态")
    )
    
    message:str = Field(
        title=_("状态说明")
    )
        
@api.delete("/tenant/{tenant_id}/users/{id}/",response=UserDeleteOutSchema, tags=['用户'], auth=None)
@operation(UserDeleteOutSchema)
def user_delete(request, tenant_id: str,id:str,data: UserDeleteInSchema=Query(...)):
    status = True,
    message = ""
    try:
        user = User.expand_objects.get(tenant__id=tenant_id,id=id)
        user.delete()
    except User.DoesNotExist as uerr:
        status = False
        message= _("指定的用户不存在。")
        logger.error(uerr)
    except Exception as err:
        status = False
        message= f'{_("删除用户失败")}:{str(err)}'
        logger.error(message)
    return {
        "status": status,
        "message": message
    }
        
# ------------- 更新用户接口 --------------
class UserUpdateInSchema(ModelSchema):
    class Config:
        model = User
        model_fields = ['avatar']

class UserUpdateInQuerySchema(Schema):
    pass
        
class UserUpdateOutSchema(Schema):
    status:bool = Field(
        title=_("状态")
    )
    
    message:str = Field(
        title=_("状态说明")
    )
        
@api.put("/tenant/{tenant_id}/users/{id}/",response=UserUpdateOutSchema, tags=['用户'], auth=None)
@operation(UserUpdateOutSchema)
def user_update(request, tenant_id: str,id:str,data:UserUpdateInSchema,query_data: UserUpdateInQuerySchema=Query(...)):
    status = True,
    message = ""
    try:
        user = User.expand_objects.get(tenant__id=tenant_id,id=id)
        user.avatar = data.avatar
        user.save()
    except User.DoesNotExist:
        status = False
        message= _("指定的用户不存在。")
        logger.error(message)
    except Exception as e:
        status = False
        message= f'{_("更新用户失败")}:{str(e)}'
        logger.error(message)
    finally:
        return {
            "status": status,
            "message": message
        }
        
# ------------- 获取用户接口 --------------
class UserInSchema(Schema):
    pass

class UserOutSchema(ModelSchema):
     class Config:
        model = User
        model_fields = ['id', 'username', 'avatar', 'is_platform_user']
        
@api.get("/tenant/{tenant_id}/users/{id}/",response=UserOutSchema, tags=['用户'], auth=None)
@operation(UserOutSchema)
def user_list(request, tenant_id: str,id:str,data: UserInSchema=Query(...)):
    user = User.expand_objects.get(tenant__id=tenant_id,id=id)
    return user


@api.get("/tenant/{tenant_id}/users/{user_id}/permissions/",tags=[_("用户")])
def get_user_permissions(request, tenant_id: str,user_id:str):
    """ 用户权限列表,TODO
    """
    return []

@api.post("/tenant/{tenant_id}/users/{user_id}/permissions/",tags=[_("用户")])
def update_user_permissions(request, tenant_id: str,user_id:str):
    """ 更新用户权限列表,TODO
    """
    return []

@api.delete("/tenant/{tenant_id}/users/{user_id}/permissions/{id}/",tags=[_("用户")])
def delete_user_permissions(request, tenant_id: str,user_id:str,id:str):
    """ 删除用户权限,TODO
    """
    return []

@api.get("/tenant/{tenant_id}/users/{user_id}/all_permissions/",tags=[_("用户")])
def get_user_all_permissions(request, tenant_id: str,user_id:str):
    """ 获取所有权限并附带是否已授权给用户状态,TODO
    """
    return []