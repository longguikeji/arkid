from logging import PlaceHolder
from typing import List, Optional
from uuid import UUID
from ninja import Field, Schema
from arkid.config import get_app_config
from arkid.core.extension import create_extension_schema
from arkid.core.extension.auth_factor import BaseAuthFactorSchema
from arkid.core.schema import ResponseSchema
from arkid.core.translation import gettext_default as _

class SendEmailCodeIn(Schema):
    email:str = Field(
        title=_("邮箱")
    )
class SendEmailCodeOut(ResponseSchema):
    pass

class MineEmailItemOut(Schema):
    
    current_email:Optional[str] = Field(
        title=_("当前邮箱账号"),
        readonly=True
    )
    
    email:str = Field(
        title=_('新邮箱账号'),
        suffix_action={
            "path":get_app_config().get_host() + "/api/v1/tenant/{tenant_id}/com_longgui_auth_factor_email/config/{config_id}/send_email_code/",
            "method":"post",
            "delay":60,
            "name":_("发送验证码")
        }
    )
    
    config_id:str = Field(
        default="",
        hidden=True
    )
    
    code:str = Field(
        title=_("验证码"),
        default=""
    )
    
class MineEmailBaseOut(ResponseSchema):
    data: Optional[MineEmailItemOut]

class UpdateMineEmailBaseIn(Schema):
    """ 更新邮箱账号参数Schema描述类

    注意： 此处因需要部分运行时配置参数故而临时写在此处，未来可能优化
    """
    email:str = Field(
        title=_('邮箱账号'),
        suffix_action={
            "path":get_app_config().get_host() + "/api/v1/tenant/{tenant_id}/com_longgui_auth_factor_email/config/{config_id}/send_email_code/",
            "method":"post",
            "delay":60,
            "name":_("发送验证码")
        }
    )
    
    config_id:str = Field(
        hidden=True
    )
    
    code:str = Field(
        title=_("验证码"),
    )
    
class UpdateMineEmailBaseOut(ResponseSchema):
    pass


MineEmailOut = create_extension_schema(
    "MineEmailOut",
    __file__,
    base_schema=MineEmailBaseOut
)

UpdateMineEmailOut = create_extension_schema(
    'UpdateMineEmailOut',
    __file__,
    base_schema=UpdateMineEmailBaseOut
)

UpdateMineEmailIn = create_extension_schema(
    'UpdateMineEmailIn',
    __file__,
    base_schema=UpdateMineEmailBaseIn
)
        