"""
SAML
"""
# pylint: disable=invalid-name
from django.urls import path

from djangosaml2idp import idpview
from djangosaml2idp import dev as dev_views

app_name = 'djangosaml2idp'

base_urlpatterns = [
    path('sso/post/', idpview.sso_entry, name="saml_login_post"),
    path('sso/redirect/', idpview.sso_entry, name="saml_login_redirect"),
    # path('sso/init', idpview.SSOInitView.as_view(), name="saml_idp_init"),
    path('login/process/', idpview.LoginProcessView.as_view(), name='saml_login_process'),
    # path('login/process_multi_factor/', idpview.ProcessMultiFactorView.as_view(), name='saml_multi_factor'),
    path('metadata/', idpview.metadata, name='saml2_idp_metadata'),
    path('download/metadata/', idpview.download_metadata, name='saml2_idp_download_metadata'),
    path('aliyun/sso-role/login/', idpview.AliyunSSORoleView.as_view(), name='aliyun_sso_role_login'),
    path('aliyun/sso-role/', idpview.AliyunSSORoleListCreateAPIView.as_view(), name='aliyun_sso_role_list'),
    path('aliyun/sso-role/<str:username>/',
         idpview.AliyunSSORoleDetailCreateAPIView.as_view(),
         name='aliyun_sso_role_detail'),
]

fe_urlpatterns = [
    path('fe/login/', dev_views.LoginView.as_view(), name='fe_login'),
    path('aliyun/sso-role/fe/login/', dev_views.AliyunRoleSSOLoginView.as_view(), name='aliyun_sso_role_fe_login'),
]

urlpatterns = base_urlpatterns + fe_urlpatterns
