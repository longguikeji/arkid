from ninja import Field, Schema
from arkid.core.extension import create_extension_schema
from arkid.core.schema import ResponseSchema
from arkid.core.translation import gettext_default as _

class GenrateAuthCodeDataOut(Schema):
    
    image: str = Field(
        title=_("图片路径")
    )
    
    authcode_key: str = Field(
        title=_("验证码key")
    )

class GenrateAuthCodeBaseOut(ResponseSchema):
    
    data: GenrateAuthCodeDataOut
    
GenrateAuthCodeOut = create_extension_schema(
    "GenrateAuthCodeOutSchema",
    __file__,
    base_schema=GenrateAuthCodeBaseOut
)
    
class CheckAuthCodeBaseIn(Schema):
    authcode_key: str = Field(
        title=_("验证码key")
    )
    
    authcode: str = Field(
        title=_("验证码")
    )
    
CheckAuthCodeIn = create_extension_schema(
    "CheckAuthCodeIn",
    __file__,
    base_schema=CheckAuthCodeBaseIn
)

CheckAuthCodeOut = create_extension_schema(
    "CheckAuthCodeOut",
    __file__,
    base_schema=ResponseSchema
)