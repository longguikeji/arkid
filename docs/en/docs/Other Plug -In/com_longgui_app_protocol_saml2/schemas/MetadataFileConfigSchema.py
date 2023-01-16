from typing import Optional
from ninja import Field,Schema
from arkid.core.translation import gettext_default as _


class MetadataFileConfigSchema(Schema):

    sp_metadata:str = Field(
        format="binary",
        hint=_("请选择上传SP METADATA文件"),
        title=_("SP METADATA文件"),
        require=True
    )
    
    attribute_mapping:dict = Field(
        format="custom_dict",
        hint=_("请添加自定义属性"),
        label=_("自定义属性"),
        default={},
        required=False
    )
    
    idp_sso_url:Optional[str] = Field(
        readonly=True,
        required=False,
        title=_("IDP SSO url")
    )
    
    idp_metadata:Optional[str] = Field(
        title=_("IDP Entity ID"),
        format="download",
        required=False,
        readonly=True
    )