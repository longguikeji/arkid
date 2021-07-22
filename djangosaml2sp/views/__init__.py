"""
SAML2.0视图集合
"""
from .MetadataView import metadata
from .MatadataDownloadView import download_metadata
from .LoginView import Login


__all__ = [
    "metadata",
    "download_metadata",
    "Login"
]
