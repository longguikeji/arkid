from .CertConfigSchema import CertConfigSchema
from ..constants import package
from arkid.core.extension import create_extension_schema

Saml2SPCertConfigSchema = create_extension_schema(
    'Saml2SPCertConfigSchema',
    package,
    base_schema=CertConfigSchema
)

__all__ = [
    "Saml2SPCertConfigSchema",
]