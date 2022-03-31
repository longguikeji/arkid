from django.urls import path
from . import views as saas_views

from django.conf.urls import url
from django.urls import re_path
from oauth2_provider import views


base_urlpatterns = [
    url(r"oauth/authorize/$", views.AuthorizationView.as_view(), name="authorize-platform"),
    url(r"oauth/token/$", views.TokenView.as_view(), name="token-platform"),
    url(r"oauth/revoke_token/$", views.RevokeTokenView.as_view(), name="revoke-token-platform"),
    url(r"oauth/introspect/$", views.IntrospectTokenView.as_view(), name="introspect-platform"),
]

oidc_urlpatterns = [
    url(r".well-known/openid-configuration/$", views.ConnectDiscoveryInfoView.as_view(), name="oidc-connect-discovery-info-platform",),
    url(r"oauth/userinfo/$", views.UserInfoExtendView.as_view(), name="oauth-user-info-platform"),
    url(r"oidc/logout/$", views.OIDCLogoutView.as_view(), name="oauth-user-logout-platform"),
    re_path(r".well-known/jwks.json$", views.JwksInfoView.as_view(), name="jwks-info-platform"),
    re_path(r"userinfo/$", views.UserInfoView.as_view(), name="user-info-platform"),
]

saas_urlpatterns = [
    path("arkid/saas/bind", saas_views.ArkIDBindAPIView.as_view(), name="bind"),
    path("arkid/saas/unbind", saas_views.ArkIDUnBindView.as_view(), name="unbind"),
]

urlpatterns = base_urlpatterns + oidc_urlpatterns + saas_urlpatterns
