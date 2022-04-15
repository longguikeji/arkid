from ninja import Schema, ModelSchema
from arkid.core.models import User
from typing import Optional


class UserSchemaOut(ModelSchema):
    class Config:
        model = User
        model_fields = ['id', 'username']

    # @staticmethod
    # def resolve_id(obj):
    #     return obj.id.replace('-', '')


class ResponseSchema(Schema):
    error: Optional[str]
    message: Optional[str]
    data: Optional[dict]
