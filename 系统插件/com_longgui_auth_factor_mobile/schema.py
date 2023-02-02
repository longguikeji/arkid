from typing import Optional
from uuid import UUID
from ninja import Field, ModelSchema, Schema
from arkid.config import get_app_config
from arkid.core import actions
from arkid.core.extension import create_extension_schema
from arkid.core.schema import ResponseSchema
from arkid.core.translation import gettext_default as _
    



class MobileAuthFactorConfigSchema(Schema):
    
    id:str = Field(
        hidden=True,
    )
    
    name:str
    
    package:str = Field(
        hidden=True
    )

class SendSMSCodeIn(Schema):
    areacode:Optional[str] = Field(
        title=_("区号"),
        default="86"
    )
    
    mobile:str = Field(
        title=_("电话号码")
    )
class SendSMSCodeOut(ResponseSchema):
    pass


class MineMobileItemOut(Schema):
    
    # areacode:str = Field(
    #     title=_("区号"),
    #     default="86"
    # )
    
    current_mobile:Optional[str] = Field(
        title=_("当前手机号码"),
        readonly=True
    )
    
    mobile:str = Field(
        title=_('新手机号码'),
        suffix_action={
            "path":get_app_config().get_host() + "/api/v1/tenant/{tenant_id}/com_longgui_auth_factor_mobile/config/{config_id}/send_sms_code/",
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
    
class MineMobileBaseOut(ResponseSchema):
    data: Optional[MineMobileItemOut]

class UpdateMineMobileBaseIn(Schema):
    """ 更新手机号码参数Schema描述类

    注意： 此处因需要部分运行时配置参数故而临时写在此处，未来可能优化
    """
    mobile:str = Field(
        title=_('手机号码'),
        suffix_action={
            "path":get_app_config().get_host() + "/api/v1/tenant/{tenant_id}/com_longgui_auth_factor_mobile/config/{config_id}/send_sms_code/",
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
    
class UpdateMineMobileBaseOut(ResponseSchema):
    pass


MineMobileOut = create_extension_schema(
    "MineMobileOut",
    __file__,
    base_schema=MineMobileBaseOut
)

UpdateMineMobileOut = create_extension_schema(
    'UpdateMineMobileOut',
    __file__,
    base_schema=UpdateMineMobileBaseOut
)

UpdateMineMobileIn = create_extension_schema(
    'UpdateMineMobileIn',
    __file__,
    base_schema=UpdateMineMobileBaseIn
)
            