
from .models import *
from uuid import UUID
from typing import List
from pydantic import Field
from ninja import ModelSchema, Schema
from arkid.core.schema import ResponseSchema
from arkid.core.translation import gettext_default as _

class CustomFieldQueryIn(Schema):

    subject: str = Field(hidden=True, default='user')

class CustomFieldItemOut(ModelSchema):

    id: UUID = Field(hidden=True)

    class Config:
        model = CustomField
        model_fields = ['id', 'name']

class CustomFieldListOut(ResponseSchema):
    data: List[CustomFieldItemOut]

class CustomFieldOut(ResponseSchema):
    data: CustomFieldItemOut

class CustomFieldIn(Schema):

    name: str = Field(title=_('name', '字段名称'), notranslation=True)
