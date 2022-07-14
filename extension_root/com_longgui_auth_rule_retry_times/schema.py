from ninja import Field, Schema

class SecondAuthFactorConfigSchema(Schema):
    
    id:str = Field(
        hidden=True,
    )
    
    name:str
    
    package:str = Field(
        hidden=True
    )