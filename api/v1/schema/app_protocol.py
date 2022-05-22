from arkid.core.models import Extension
from arkid.core.schema import ResponseSchema
from typing import List
from ninja import Field, Schema
from arkid.core.translation import gettext_default as _

class AppProtocolListItemOut(Schema):
    name: str = Field(
        title=_("协议名称")
    )
    
    doc_url: str = Field(
        title=_("文档")
    )
    
    package: str = Field(
        title=_("来源")
    )
    
    description: str = Field(
        title=_("描述")
    )
    
class AppProtocolListOut(ResponseSchema):
    data: List[AppProtocolListItemOut]