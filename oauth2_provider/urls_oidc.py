from django.conf.urls import url

from oauth2_provider import views
from oauth2_provider.views import dev as dev_views

from django.views.decorators.csrf import csrf_exempt


app_name = "oidc_provider"


urlpatterns = [
    url(r"^_authorize/$", views.AuthorizationView.as_view(), name="oidc_authorize"),
    url(r"^authorize/$", views.AuthorizationWraperView.as_view(), name="oidc_authorize_wraper"),
    url(r"^token/$", views.TokenView.as_view(), name="oidc_token"),
    url(r"^revoke_token/$", views.RevokeTokenView.as_view(), name="oidc_revoke-token"),
    url(r"^introspect/$", views.OidcIntrospectTokenView.as_view(), name="oidc_introspect"),
    url(r'^userinfo/$', views.UserInfoOidcView.as_view(), name="oidc_userinfo"),
    url(r'^jwks/$', views.JwksView.as_view(), name="oidc_jwks"),
    url(r'^\.well-known/openid-configuration/$', views.OidcProviderInfoView.as_view(),
        name='oidc_provider-info'),
]

