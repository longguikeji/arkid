"""
SAML2.0协议IDP 插件路由
"""

from django.urls import path

from djangosaml2sp.views import metadata, download_metadata,Login,AssertionConsumerService

urlpatterns = [
    path(
        'sp_metadata/',
        metadata,
        name="sp_metadata"
    ),
    path(
        'sp_download_metadata/',
        download_metadata,
        name="sp_download_metadata"
    ),
    path(
        'sp_login/',
        Login.as_view(),
        name="sp_login"
    ),
    path(
        'acs/',
        AssertionConsumerService.as_view(),
        name="sp_acs"
    ),
]
