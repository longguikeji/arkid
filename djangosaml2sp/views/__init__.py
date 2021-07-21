"""
SAML2.0视图集合
"""
from .MetadataView import metadata
from .MatadataDownloadView import download_metadata


__all__ = [
    "metadata",
    "download_metadata",
]
