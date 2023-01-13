from typing import Optional
from ninja import Field,Schema
from arkid.core.translation import gettext_default as _


class AliyunRamSchema(Schema):

    sp_metadata:str = Field(
        format="binary",
        hint=_("请选择上传SP METADATA文件"),
        title=_("SP METADATA文件"),
        required=True
    )
    
    auxiliary_domain:str = Field(
        required=True,
        title=_("辅助域名"),
    )
    
    idp_sso_url:Optional[str] = Field(
        readonly=True,
        title=_("IDP SSO url"),
        required=False
    )
    
    idp_metadata:Optional[str] = Field(
        title=_("IDP Entity ID"),
        format="download",
        readonly=True,
        required=False
    )