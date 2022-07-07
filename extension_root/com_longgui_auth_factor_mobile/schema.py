from typing import Optional
from uuid import UUID
from ninja import Field, ModelSchema, Schema
from arkid.core import actions
from arkid.core.actions import DirectAction
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


class UpdateMineMobileBaseIn(Schema):
    """ 更新手机号码参数Schema描述类

    注意： 此处因需要部分运行时配置参数故而临时写在此处，未来可能优化
    """
    mobile:str = Field(
        title='手机号',
        suffix_action=DirectAction(
            name='发送验证码',
            # path=self.url_send_sms_code,
            method=actions.FrontActionMethod.POST,
            params={
                "mobile": "mobile",
                "areacode": "86",
            },
            delay=60,
        ).dict()
    )
    
    code:str = Field(title='验证码')

class UpdateMineMobileBaseOut(ResponseSchema):
    pass


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
            