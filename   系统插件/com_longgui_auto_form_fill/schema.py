
from enum import Enum
from uuid import UUID
from ninja import Schema, ModelSchema
from typing import List
from arkid.core.schema import ResponseSchema
from arkid.core.translation import gettext_default as _
from arkid.core import pages, actions
from typing import Optional
from pydantic import Field
from uuid import UUID
from .models import *

class SAVE_TYPE(str, Enum):
    database = _('database', '数据库')
    web = _('web', '浏览器')

class Account_Type(str, Enum):
    mobile_email = _('mobile_email', '电话和邮箱')
    mobile = _('mobile', '电话')
    email = _('email', '邮箱')
    no_limit = _('no limit', '不限制')

class AutoFormFillSettingsConfigSchema(Schema):

    save_type: SAVE_TYPE = Field(default='web', title=_('Save Type', '存储位置'))

class AutoFormFillUserQueryIn(Schema):

    username: Optional[str] = Field(title=_('Username', '用户名'))

class AutoFormFillUserItemOut(ModelSchema):

    id: UUID = Field(hidden=True)
    app_name: str = Field(alias='app.name', title=_('App Name', '应用'))
    belong_to_user: str = Field(alias='user.username', title=_('Belong to Username', '所属用户'))
    username: str = Field(title=_('Account Name', '账户'))

    class Config:
        model = AutoFormFillUser
        model_fields = ['id']

class AutoFormFillUserListOut(ResponseSchema):
    data: List[AutoFormFillUserItemOut]


# 选择应用页面
select_app_page = pages.TablePage(select=True,name=_("选择应用"))

pages.register_front_pages(select_app_page)

select_app_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/apps/?type=AutoFormFill',
        method=actions.FrontActionMethod.GET
    )
)
# 选择用户页面
select_user_page = pages.TablePage(select=True,name=_("选择用户"))

pages.register_front_pages(select_user_page)

select_user_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/users/',
        method=actions.FrontActionMethod.GET
    )
)

class AutoFormFillUserAppSelectSchemaIn(Schema):

    id:UUID = Field(hidden=True)
    name:str

class AutoFormFillUserSelectSchemaIn(Schema):

    id:UUID = Field(hidden=True)
    username:str

class AutoFormFillUserIn(Schema):

    app: AutoFormFillUserAppSelectSchemaIn = Field(
        page=select_app_page.tag,
        title=_("应用")
    )
    user: AutoFormFillUserSelectSchemaIn = Field(
        page=select_user_page.tag,
        title=_("用户")
    )
    username: str = Field(title=_('Account Name', '账户'), placeholder_url='/api/v1/com_longgui_auto_form_fill/apps/{app_id}/get_app_placeholder/',placeholder_url_params={'app_id':'app.id'})
    password: str = Field(title=_('Password', '密码'))

class AutoFormFillUserDetailItemOut(ModelSchema):

    id: UUID = Field(hidden=True)
    app: AutoFormFillUserAppSelectSchemaIn = Field(
        page=select_app_page.tag,
        title=_("应用")
    )
    user: AutoFormFillUserSelectSchemaIn = Field(
        page=select_user_page.tag,
        title=_("用户")
    )
    username: str = Field(title=_('Account Name', '账户'))
    password: Optional[str] = Field(title=_('Password', '密码'), default='')

    @staticmethod
    def resolve_password(obj):
        return ''

    class Config:
        model = AutoFormFillUser
        model_fields = ['id']

class AutoFormFillUserOut(ResponseSchema):
    data: AutoFormFillUserDetailItemOut


######### 我的

class AutoFormFillUserMineItemOut(ModelSchema):

    id: UUID = Field(hidden=True)
    app_name: str = Field(alias='app.name', title=_('App Name', '应用'))
    username: str = Field(title=_('Account Name', '账户'))

    class Config:
        model = AutoFormFillUser
        model_fields = ['id']

class AutoFormFillUserMineListOut(ResponseSchema):
    data: List[AutoFormFillUserMineItemOut]

class AutoFormFillUserMineIn(Schema):

    username: str = Field(title=_('Account Name', '账户'), placeholder_url='/api/v1/com_longgui_auto_form_fill/apps/{app_id}/get_app_placeholder/',placeholder_url_params={'app_id':'app.id'})
    password: str = Field(title=_('password', '密码'))
    app: AutoFormFillUserAppSelectSchemaIn = Field(
        page=select_app_page.tag,
        title=_("应用")
    )

class AutoFormFillUserUpdateIn(Schema):

    password: str = Field(title=_('password', '密码'))

class AutoFormFillUserDetailItemMineOut(ModelSchema):

    id: UUID = Field(hidden=True)
    username: str = Field(title=_('Account Name', '账户'))
    password: Optional[str] = Field(title=_('password', '密码'), default='')
    app: AutoFormFillUserAppSelectSchemaIn = Field(
        page=select_app_page.tag,
        title=_("应用")
    )

    @staticmethod
    def resolve_password(obj):
        return ''

    class Config:
        model = AutoFormFillUser
        model_fields = ['id',]

class AutoFormFillUserMineOut(ResponseSchema):
    data: AutoFormFillUserDetailItemMineOut

class AutoFormFillUserApiIn(Schema):

    username: str = Field(title=_('Account Name', '账户'))
    password: str = Field(title=_('password', '密码'))