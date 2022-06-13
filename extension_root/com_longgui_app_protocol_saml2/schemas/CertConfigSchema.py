from django.forms import FileField
from ninja import Field,UploadedFile
from pkg_resources import require
from .BaseConfigSchema import BaseConfigSchema
from arkid.core.translation import gettext_default as _


class CertConfigSchema(BaseConfigSchema):

    sp_entity_id:str = Field(
        title=_("SP Entity ID")
    )

    sp_acs:str = Field(
        title=_("SP ACS")
    )

    sp_sls:str = Field(
        title=_("SP SLS")
    )

    sp_cert:str = Field(
        format="binary",
        hint=_("请选择上传SP 加密公钥"),
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