from uuid import UUID
from arkid.core.schema import ResponseSchema
from ninja import ModelSchema, Schema
from typing import List, Optional
from arkid.core.models import App, AppGroup, Message, Tenant, User, Permission
from pydantic import Field
from arkid.core import pages,actions
from arkid.core.translation import gettext_default as _


class MineAppItem(ModelSchema):
    class Config:
        model = App
        model_fields = ['id', 'logo', 'name','url','description','type']
class MineAppsOut(ResponseSchema):
    data:Optional[List[MineAppItem]]


class ProfileTenantOut(Schema):

    id:UUID = Field(title='ID', hidden=True)

    slug:Optional[str] = Field(title='slug', hidden=True)

    name:str = Field(title='name', hidden=True)
    
    is_platform_tenant:bool = Field(title=_("是否是平台租户"),hidden=True,default=False,readonly=True)

class ProfileSchemaOut(Schema):
    
    id:UUID = Field(title='ID', hidden=True)
    username:str = Field(title='用户名',readonly=True)
    avatar:Optional[str] = Field(title=_('头像'))
    tenant:ProfileTenantOut = Field(title=_("租户"),hidden=True)

class ProfileSchemaFinalOut(ResponseSchema):
    data:Optional[ProfileSchemaOut]
class ProfileSchemaIn(ModelSchema):
    class Config:
        model = User
        model_fields = ['avatar']


class MineTenantListItemOut(ModelSchema):
    class Config:
        model = Tenant
        model_fields = ["id", "name", "slug", "icon"]

class MinePermissionListSchemaOut(Schema):

    id: UUID = Field(hidden=True)
    name: str
    # app_name: str = Field(default=None, alias="app.name", title=_("应用名称"))
    category: str
    sort_id: int = Field(hidden=True)
    in_current: bool = Field(item_action={"path":"/api/v1/mine/tenant/{tenant_id}/permissions/{permission_id}/add_permisssion", "method":actions.FrontActionMethod.GET.value, "close": False})
    # is_system: bool
    # is_open: bool = Field(item_action={"path":"/api/v1/tenant/{tenant_id}/permission/{id}/toggle_open", "method":actions.FrontActionMethod.POST.value})

    # class Config:
    #     model = Permission
    #     model_fields = ['id', 'name', 'category', 'is_system']


class MineTenantListOut(ResponseSchema):
    data: List[MineTenantListItemOut]


class MineLogoutOut(ResponseSchema):
    
    refresh:bool = Field(
        title=_("是否刷新页面")
    )
    
class MineSwitchTenantItem(Schema):
    
    id:str = Field(
        title=_("租户ID")
    )
    
    slug:Optional[str] = Field(
        title=_("租户SLUG")
    )
class MineSwitchTenantOut(ResponseSchema):
    
    refresh:bool = Field(
        title=_("是否刷新页面")
    )
    
    switch_tenant: MineSwitchTenantItem = Field(
        title=_("切换租户")
    )
    
class MineAppGroupListItemOut(ModelSchema):
    class Config:
        model = AppGroup
        model_fields = ['id', 'name']
        
class MineAppGroupListOut(ResponseSchema):
    data:List[MineAppGroupListItemOut]
    
class MineAppListItemOut(ModelSchema):
    class Config:
        model = App
        model_fields = ['id', 'logo', 'name','url','description','type']
        
class MineAppListOut(ResponseSchema):
    data:List[MineAppListItemOut]
    

class MessageSenderItemOut(Schema):
    
    avatar:str=Field(
        title=_("头像")
    )
        
    name:str = Field(
        title=_("发送者")
    )
    
    id:str = Field(
        hidden=True
    )
    
class MessageSenderOut(ResponseSchema):
    data:List[MessageSenderItemOut]

class MineMessageListItemOut(ModelSchema):
    class Config:
        model = Message
        model_fields = ["id","title","content","created"]
    
    title:str=Field(
        title=_("标题")
    )
    
    content:str = Field(
        title=_("内容"),
    )
    
    created:str = Field(
        title=_("送达时间")
    )
    
    sender_id:str = Field(
        hidden=True
    )
    
    user_id:str =Field(
        hidden=True
    )
    
    sender_name:str = Field(
        hidden=True
    )
    
    user_name:str =Field(
        hidden=True
    )
    
    sender_avatar:str = Field(
        hidden=True
    )
    
    user_avatar:str =Field(
        hidden=True
    )
    
    readed_status_str:str = Field(
        title=_("阅读状态")
    )
    
    @staticmethod
    def resolve_readed_status_str(obj):
        if obj.readed_status:
            return _("已读")
        else:
            return _("未读")
        
    
    @staticmethod
    def resolve_sender_id(obj):
        return obj.sender.id.hex if obj.sender else "0"
    
    @staticmethod
    def resolve_user_id(obj):
        return obj.user.id.hex
    
    @staticmethod
    def resolve_sender_name(obj):
        return obj.sender.username if obj.sender else _("系统")
    
    @staticmethod
    def resolve_user_name(obj):
        return obj.user.username
    
    @staticmethod
    def resolve_sender_avatar(obj):
        return obj.sender.avatar if obj.sender else ""
    
    @staticmethod
    def resolve_user_avatar(obj):
        return obj.user.avatar
    
    @staticmethod
    def resolve_created(obj):
        return obj.created.strftime('%Y-%m-%d %H:%M:%S')
    
    @staticmethod
    def resolve_content(obj):
        return obj.content[:200]
        
class MineMessageListOut(ResponseSchema):
    data:List[MineMessageListItemOut]
    
class MineMessageItemOut(ModelSchema):
    class Config:
        model=Message
        model_fields = ["id","title","content","created","url"]
    id:UUID = Field(
        hidden=True
    )
    title:str = Field(
        title=_("标题"),
        readonly=True
    )
    content:str = Field(
        format="textarea",
        title=_("内容"),
        max_length=65336,
        readonly=True
    )
    
    url:str = Field(
        format="redirect",
        title=_("详情链接"),
        readonly=True
    )
    
    created:str = Field(
        title=_("送达时间"),
        readonly=True
    )

    @staticmethod
    def resolve_created(obj):
        return obj.created.strftime('%Y-%m-%d %H:%M:%S')
    
class MineMessageOut(ResponseSchema):
    data:MineMessageItemOut

class MineBindAccountItem(Schema):

    id: UUID
    name: str = Field(default='', title=_('名称'))
    nickname: str = Field(default='', title=_('昵称'))
    avatar: str = Field(default='', title=_('头像'))


class MineBindAccountOut(ResponseSchema):
    data:List[MineBindAccountItem]


class MineUnBindAccountItem(Schema):

    id: UUID
    name: str = Field(default='', title=_('名称'))


class MineUnBindAccountOut(ResponseSchema):
    data:List[MineUnBindAccountItem]
    
class MineUnreadedMessageCountItemOut(Schema):
    count:int =Field(
        title=_("未读消息数量"),
        default=0
    )
    
class MineUnreadedMessageCountOut(ResponseSchema):
    data:MineUnreadedMessageCountItemOut