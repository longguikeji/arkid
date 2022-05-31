from typing import List, Optional
from uuid import UUID
from ninja import Field, ModelSchema, Schema
from arkid.core.translation import gettext_default as _
from arkid.core.models import Tenant
from arkid.core.schema import ResponseSchema

class UploadItemOut(Schema):
    url:str = Field(
        title=_("文件链接")
    )

class UploadOut(ResponseSchema):
    data:UploadItemOut