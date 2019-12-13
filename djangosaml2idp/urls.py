'''
SAML
'''
from django.urls import path

from djangosaml2idp import idpview

app_name = 'djangosaml2idp'    # pylint: disable=invalid-name

urlpatterns = [    # pylint: disable=invalid-name
    path('sso/post', idpview.sso_entry, name="saml_login_post"),
    path('sso/redirect', idpview.sso_entry, name="saml_login_redirect"),
    # path('sso/init', idpview.SSOInitView.as_view(), name="saml_idp_init"),
    path('login/process/', idpview.LoginProcessView.as_view(), name='saml_login_process'),
    # path('login/process_multi_factor/', idpview.ProcessMultiFactorView.as_view(), name='saml_multi_factor'),
    path('metadata', idpview.metadata, name='saml2_idp_metadata'),
    path('download/metadata', idpview.download_metadata, name='saml2_idp_download_metadata'),
]
