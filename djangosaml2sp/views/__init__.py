"""
SAML2.0视图集合
"""
from .MetadataView import metadata
from .MatadataDownloadView import download_metadata
from .LoginView import Login
from .AssertionConsumerServiceView import AssertionConsumerService


__all__ = [
    "metadata",
    "download_metadata",
    "Login",
    "AssertionConsumerService"
]
