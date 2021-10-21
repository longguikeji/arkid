"""
SAML2.0协议IDP 插件路由
"""

from django.urls import re_path

from djangosaml2idp.views import SSOEntry, metadata, download_metadata, SsoHook, SAML2LoginProcess, FakeLogin,SSOInit

urlpatterns = [
    re_path(
        r'app/(?P<app_id>[\w-]+)/sso/post/',
        SSOEntry.as_view(),
        name="saml_login_post"
    ),
    re_path(
        r'app/(?P<app_id>[\w-]+)/sso/redirect/',
        SSOEntry.as_view(),
        name="saml_login_redirect"
    ),
    re_path(
        r'app/(?P<app_id>[\w-]+)/metadata/',
        metadata,
        name="metadata"
    ),
    re_path(
        r'app/(?P<app_id>[\w-]+)/download/metadata/',
        download_metadata,
        name="download_metadata"
    ),
    re_path(
        r'app/(?P<app_id>[\w-]+)/hook/',
        SsoHook.as_view(),
        name="saml_sso_hook"
    ),
    re_path(
        r'app/(?P<app_id>[\w-]+)/saml_login_process/',
        SAML2LoginProcess.as_view(),
        name="saml_login_process"
    ),
    re_path(
        r'app/(?P<app_id>[\w-]+)/fake_login/',
        FakeLogin.as_view(),
        name="fake_login"
    ),
    re_path(
        r'app/(?P<app_id>[\w-]+)/sso_init/',
        SSOInit.as_view(),
        name="sso_init"
    ),
]
