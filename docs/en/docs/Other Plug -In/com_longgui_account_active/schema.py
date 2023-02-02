from typing import List, Optional
from ninja import Field, Schema
from api.v1.schema.user import UserListItemOut
from arkid.core.extension import create_extension_schema
from arkid.core.schema import ResponseSchema
from arkid.core.translation import gettext_default as _

class AccountActiveSwitchOutItemSchema(Schema):
    is_active:bool = Field(
        _("是否活跃账户"),
    )

class AccountActiveSwitchOutBaseSchema(ResponseSchema):
    
    data:Optional[AccountActiveSwitchOutItemSchema]
    
AccountActiveSwitchOut = create_extension_schema(
    "AccountActiveSwitchOut",
    __file__,
    base_schema=AccountActiveSwitchOutBaseSchema
)


class InactiveAccountListOutBaseSchema(ResponseSchema):
    
    data:Optional[List[UserListItemOut]]

InactiveAccountListOut = create_extension_schema(
    "InactiveAccountListOut",
    __file__,
    base_schema=InactiveAccountListOutBaseSchema
)
