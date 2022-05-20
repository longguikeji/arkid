from arkid.core.models import Extension
from arkid.core.schema import ResponseSchema
from typing import List
from ninja import Schema

class AppProtocolListItemOut(Schema):
    id: str
    name: str
    package: str

class AppProtocolListOut(ResponseSchema):
    data: List[AppProtocolListItemOut]