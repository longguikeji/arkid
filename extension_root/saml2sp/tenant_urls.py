"""
SAML2.0协议IDP 插件路由
"""

from django.urls import path

from djangosaml2sp.views import metadata, download_metadata

urlpatterns = [
    path(
        'metadata/',
        metadata,
        name="sp_metadata"
    ),
    path(
        'metadata/',
        download_metadata,
        name="sp_download_metadata"
    ),
]
