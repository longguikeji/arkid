from ninja import ModelSchema
from arkid.core.schema import ResponseSchema
from .models import UserMobile

class MineMobileItemOut(ModelSchema):
    class Config:
        model=UserMobile
        model_fields=['mobile']

class MineMobileOut(ResponseSchema):
    
    data = MineMobileItemOut
    
class UpdateMineMobileIn(ModelSchema):
    class Config:
        model=UserMobile
        model_fields=['mobile']
    
class UpdateMineMobileOut(ResponseSchema):
    pass