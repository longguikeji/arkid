from typing import Optional
from ninja import Field, Schema
from arkid.core.translation import gettext_default as _


class CertConfigSchema(Schema):

    sp_entity_id:str = Field(
        title=_("SP Entity ID")
    )

    sp_acs:str = Field(
        title=_("SP ACS")
    )

    sp_sls:Optional[str] = Field(
        title=_("SP SLS")
    )

    sp_cert:str = Field(
        format="binary",
        hint=_("请选择上传SP 证书"),
        title=_("SP CERT"),
        require=True
    )
    
    encrypt_saml_responses:bool = Field(
        default=False
    )
    
    sign_response:bool = Field(
        default=False
    )
    
    sign_assertion:bool = Field(
        default=False
    )
    
    idp_sso_url:Optional[str] = Field(
        readonly=True,
        title=_("IDP SSO url"),
        required=False,
    )
    
    idp_cert:Optional[str] = Field(
        title=_("IDP 证书"),
        format="download",
        readonly=True,
        required=False,
    )
    
    idp_metadata:str = Field(
        title=_("IDP Entity ID"),
        format="download",
        readonly=True,
        required=False,
    )