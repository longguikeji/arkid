from uuid import UUID
from arkid.core.schema import ResponseSchema
from typing import List
from ninja import Field, ModelSchema, Schema
from arkid.core.translation import gettext_default as _
from arkid.core.models import LanguageData

class LanguageListItemOut(Schema):
    id:UUID
    
    name:str = Field(
        title=_("语言名称")
    )
    
    count:int = Field(
        title=_("词句数量")
    )
    
    extension_name:str  = Field(
        title=_("所属插件")
    )
    
    extension_package:str = Field(
        title=_("所属插件标识")
    )

class LanguageListOut(ResponseSchema):
    data: List[LanguageListItemOut]
    
class LanguageCreateIn(ModelSchema):
    
    class Config:
        model=LanguageData
        model_fields = ["name"]
        
class LanguageCreateOut(ResponseSchema):
    pass

class LanguageDeleteOut(ResponseSchema):
    pass

class LanguageDataItemOut(Schema):
    source:str = Field(
        title=_("原词句")
    )
    
    translated:str = Field(
        title=_("译词句")
    )
    
class LanguageDataOut(ResponseSchema):
    data: List[LanguageDataItemOut]

class LanguageDataItemCreateIn(Schema):
    source:str = Field(
        title=_("原词句"),
        path="/api/v1/tenant/{tenant_id}/translate_word/",
        method="get"
    )
    
    translated:str = Field(
        title=_("译词句")
    )

class LanguageDataItemCreateOut(ResponseSchema):
    pass

class LanguageTranslateWordOut(ResponseSchema):
    data:List[str]