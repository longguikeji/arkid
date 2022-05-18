from typing import List
from pydantic import Field
from ninja import ModelSchema, Schema
from arkid.core.translation import gettext_default as _
from arkid.core.schema import ResponseSchema
from arkid.core.models import App


class AppCreateIn(ModelSchema):

    class Config:
        model = App
        model_fields = ["name", "logo", "url", "description"]

class AppCreateOut(ResponseSchema):
    pass

class AppListItemOut(ModelSchema):
    class Config:
        model = App
        model_fields = ['id', 'name', 'url', 'logo', 'type']

class AppListOut(ResponseSchema):
    data: List[AppListItemOut]