from arkid.core.schema import ResponseSchema
from typing import List
from ninja import Field, Schema
from arkid.core.translation import gettext_default as _

class LanguageListItemOut(Schema):
    name: str
    count: int = Field(
        title=_("词句数量")
    )

class LanguageListOut(ResponseSchema):
    data: List[LanguageListItemOut]