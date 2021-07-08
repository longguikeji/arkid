"""
SAML2.0视图集合
"""

from .SAML2IDPErrorView import SAML2IDPError
from .SsoEntryView import SSOEntry
from .MetadataView import metadata
from .MatadataDownloadView import download_metadata
from .SsoHookView import SsoHook

__all__ = [
    "SSOEntry",
    "SAML2IDPError",
    "metadata",
    "download_metadata",
    "SsoHook"
]
