
from tabnanny import verbose
from typing import List
from uuid import UUID
from arkid.core import actions, pages
from arkid.core.models import Message
from ninja import ModelSchema,Field,Schema
from arkid.core.translation import gettext_default as _
from arkid.core.extension.message import MessageExtension
from arkid.core.schema import ResponseSchema

class MessageListItemOut(ModelSchema):
    class Config:
        model = Message
        model_fields = ['id', 'title','content','url','created']
        
    title:str = Field(
        title=_("标题")
    )
    
    user_name:str = Field(
        title=_("用户")
    )
    
    content:str = Field(
        title=_("内容")
    )
    
    readed_status_str:str = Field(
        title=_("阅读状态")
    )
    
    @staticmethod
    def resolve_user_name(obj):
        if obj.user:
            return obj.user.username
        else:
            return ''
        
    @staticmethod
    def resolve_readed_status_str(obj):
        if obj.readed_status:
            return _("已读")
        else:
            return _("未读")
        
    @staticmethod
    def resolve_conetent(obj):
        if len(obj.content)>20:
            return f'{obj.content[:17]}...'
        else:
            return obj.content
        
class MessageListOut(ResponseSchema):

    data: List[MessageListItemOut]

select_user_page = pages.TablePage(select=True,name=_("选择用户"))

pages.register_front_pages(select_user_page)

select_user_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/users/',
        method=actions.FrontActionMethod.GET
    )
)

class MessageCreateIn(ModelSchema):
    
    user:str = Field(
        title=_("用户"),
        page=select_user_page.tag
    )
    
    title:str = Field(
        title=_("标题")
    )
    
    content:str = Field(
        title=_("内容"),
        format="textarea"
    )
    
    class Config:
        model = Message
        model_fields = ['title','content','user']
        
class MessageCreateOut(ResponseSchema):
    pass

class MessageDeleteOut(ResponseSchema):
    pass
