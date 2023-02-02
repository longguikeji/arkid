from ninja import Field
from .schemas.CertConfigSchema import CertConfigSchema
from .schemas.MetadataFileConfigSchema import MetadataFileConfigSchema
from .schemas.AliyunRamSchema import AliyunRamSchema
from .schemas.AliyunRoleSchema import AliyunRoleSchema
from arkid.core.extension import create_extension_schema

Saml2SPCertConfigSchema = create_extension_schema(
    'Saml2SPCertConfigSchema',
    __file__,
    base_schema=CertConfigSchema
)

Saml2SPMetadataFileConfigSchema = create_extension_schema(
    'Saml2SPMetadataFileConfigSchema',
    __file__,
    base_schema=MetadataFileConfigSchema
)
Saml2SPAliyunRoleConfigSchema = create_extension_schema(
    'Saml2SPAliyunRoleConfigSchema',
    __file__,
    [("url",str,Field(readonly=True,required=False)),],
    base_schema=AliyunRoleSchema
)
Saml2SPAliyunRamConfigSchema = create_extension_schema(
    'Saml2SPAliyunRamConfigSchema',
    __file__,
    base_schema=AliyunRamSchema
)

__all__ = [
    "Saml2SPCertConfigSchema",
    "Saml2SPMetadataFileConfigSchema",
    "Saml2SPAliyunRoleConfigSchema",
    "Saml2SPAliyunRamConfigSchema"
]