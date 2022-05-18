from ninja import Schema, ModelSchema
from arkid.core.models import User
from typing import Optional


class RootSchema(Schema):
    def __iter__(self):
        return iter(self.__root__)

    def __getattr__(self, item):
        if not hasattr(self, "__root__"):
            return getattr(self, item)
        return getattr(self.__root__, item)

    def __setattr__(self, item, value):
        if not hasattr(self, "__root__"):
            return setattr(self, item, value)
        return setattr(self.__root__, item, value)

    def dict(self, **kwargs):
        if not hasattr(self, "__root__"):
            return super().dict(**kwargs)
        if isinstance(self.__root__, list):
            return [value.dict() for value in self.__root__]
        return self.__root__.dict(**kwargs)


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
