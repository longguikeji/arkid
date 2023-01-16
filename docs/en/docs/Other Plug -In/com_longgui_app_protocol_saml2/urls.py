"""
SAML2.0协议IDP 插件路由
"""

from django.urls import re_path

from .views.idp import *
urlpatterns = [
    re_path(
        r'saml2/idp/cert/',
        cert,
        name="idp_cert"
    ),
    re_path(
        r'app/(?P<config_id>[\w-]+)/saml2/idp/sso/post/',
        SSOEntry.as_view(),
        name="idp_sso_post"
    ),
    re_path(
        r'app/(?P<config_id>[\w-]+)/saml2/idp/sso/redirect/',
        SSOEntry.as_view(),
        name="idp_sso_redirect"
    ),
    re_path(
        r'app/(?P<config_id>[\w-]+)/saml2/idp/metadata/',
        metadata,
        name="idp_metadata"
    ),
    re_path(
        r'app/(?P<config_id>[\w-]+)/saml2/idp/login/',
        LoginProcess.as_view(),
        name="idp_login_process"
    ),
    re_path(
        r'app/(?P<config_id>[\w-]+)/saml2/idp/sso_init/',
        SSOInit.as_view(),
        name="idp_sso_init"
    ),
]
