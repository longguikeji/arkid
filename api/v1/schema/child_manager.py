from ninja import ModelSchema
from arkid.core.models import User

class ChildManagerListOut(ModelSchema):

    class Config:
        model = User
        model_fields = ["id","username", "avatar"]