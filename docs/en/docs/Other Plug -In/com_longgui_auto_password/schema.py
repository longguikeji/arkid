from ninja import Field, Schema


class AutoPasswordSchemaConfigSchema(Schema):
    
    id:str = Field(
        hidden=True,
    )
    
    name:str
    
    package:str = Field(
        hidden=True
    )