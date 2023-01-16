from typing import Optional
from ninja import Field,Schema
from arkid.core.translation import gettext_default as _


class AliyunRoleSchema(Schema):

    sp_metadata:str = Field(
        format="binary",
        hint=_("请选择上传SP METADATA文件"),
        title=_("SP METADATA文件"),
        required=True
    )
    
    role:str = Field(
        title=_("Role"),
        required=True,
    )
    
    role_session_name:str = Field(
        title=_("RoleSessionName"),
        required=False,
        default="username"
    )
    
    session_duration:str = Field(
        title=_("SessionDuration"),
        required=False,
        default="1800"
    )
    
    idp_sso_url:Optional[str] = Field(
        readonly=True,
        required=False,
        title=_("IDP SSO url")
    )
    
    idp_metadata:Optional[str] = Field(
        title=_("IDP Entity ID"),
        required=False,
        format="download",
        readonly=True
    )