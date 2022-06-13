from ninja import Field, Schema
from arkid.core.translation import gettext_default as _

class BaseConfigSchema(Schema):
    
    idp_cert:str = Field(
        title=_("IDP 证书"),
        format="download",
        read_only=True
    )
    
    idp_metadata:str = Field(
        title=_("IDP Entity ID"),
        format="download",
        read_only=True
    )