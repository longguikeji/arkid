from django.conf.urls import url

from oauth2_provider import views
from oauth2_provider.views import dev as dev_views

from django.views.decorators.csrf import csrf_exempt


app_name = "oauth2_provider"


base_urlpatterns = [
    url(r"^_authorize/$", views.AuthorizationView.as_view(), name="authorize"),
    url(r"^authorize/$", views.AuthorizationWraperView.as_view(), name="authorize_wraper"),
    url(r"^token/$", views.TokenView.as_view(), name="token"),
    url(r"^revoke_token/$", views.RevokeTokenView.as_view(), name="revoke-token"),
    url(r"^introspect/$", views.IntrospectTokenView.as_view(), name="introspect"),
    url(r'^userinfo/$', views.UserInfoOauthView.as_view(), name="userinfo"),
]


management_urlpatterns = [
    # Application management views
    url(r"^applications/$", views.ApplicationList.as_view(), name="list"),
    url(r"^applications/register/$", views.ApplicationRegistration.as_view(), name="register"),
    url(r"^applications/(?P<pk>[\w-]+)/$", views.ApplicationDetail.as_view(), name="detail"),
    url(r"^applications/(?P<pk>[\w-]+)/delete/$", views.ApplicationDelete.as_view(), name="delete"),
    url(r"^applications/(?P<pk>[\w-]+)/update/$", views.ApplicationUpdate.as_view(), name="update"),
    # Token management views
    url(r"^authorized_tokens/$", views.AuthorizedTokensListView.as_view(), name="authorized-token-list"),
    url(r"^authorized_tokens/(?P<pk>[\w-]+)/delete/$", views.AuthorizedTokenDeleteView.as_view(),
        name="authorized-token-delete"),
]

fe_urlpatterns = [
    url(r'^fe/login/$', dev_views.LoginView.as_view(), name='fe_login'),
    url(r'^fe/token/$', dev_views.TokenView.as_view(), name='fe_token'),
]


urlpatterns = base_urlpatterns + management_urlpatterns + fe_urlpatterns
