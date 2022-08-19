
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
    
    @staticmethod
    def resolve_user(obj):
        if obj.user:
            return obj.user.get("nickname",obj.user.username)
        else:
            return ''
        
    @staticmethod
    def resolve_source(obj):
        if obj.source:
            return obj.source.name
        else:
            return '系统'
        
    @staticmethod
    def resolve_readed_status(obj):
        if obj.readed_status:
            return _("已读")
        else:
            return _("未读")
    
    class Config:
        model = Message
        model_fields = ['id', 'title','content','user','source','created','readed_status']
        
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

class MessageExtesionConfigListItemOut(Schema):
    
    id: str
    name: str = Field(title=_("配置名称"))
    type: str = Field(title=_("中间件类型"))
    extension_name: str = Field(title=_("所属插件"))
    extension_package: str = Field(title=_("所属插件标识"))
        
class MessageExtesionConfigListOut(ResponseSchema):
    data:List[MessageExtesionConfigListItemOut]
    
class MessageExtesionConfigOut(ResponseSchema):
    data: MessageExtension.create_composite_config_schema(
        'MessageExtesionConfigOut'
    )
    
MessageExtesionConfigCreateIn = MessageExtension.create_composite_config_schema(
    'MessageExtesionConfigCreateIn',
    exclude=['id']
)

class MessageExtesionConfigCreateOut(ResponseSchema):
    pass


MessageExtesionConfigUpdateIn = MessageExtension.create_composite_config_schema(
    'MessageExtesionConfigUpdateIn'
)

class MessageExtesionConfigUpdateOut(ResponseSchema):
    pass

class MessageExtesionConfigDeleteOut(ResponseSchema):
    pass