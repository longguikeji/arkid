"""
(2) CAS server URIs as described in the CAS protocol.
"""

from django.urls import re_path

# from mama_cas.views import LoginView
from .views import LogoutView
from .views import ValidateView
from .views import ServiceValidateView
from .views import ProxyValidateView
from .views import ProxyView
from .views import WarnView
from .views import SamlValidateView


urlpatterns = [
    # re_path(r'^login/?$', LoginView.as_view(), name='cas_login'),
    re_path(r'^app/(?P<app_id>[\w-]+)/cas/logout/$', LogoutView.as_view(), name='cas_logout'),
    # re_path(r'^app/(?P<app_id>[\w-]+)/cas/verify/$', ServiceValidateView.as_view(), name='cas_verify'),
    re_path(r'^app/(?P<app_id>[\w-]+)/cas/serviceValidate/$', ServiceValidateView.as_view(), name='cas_service_validate'),
    re_path(r'^app/(?P<app_id>[\w-]+)/cas/proxyValidate/$', ProxyValidateView.as_view(), name='cas_proxy_validate'),
    re_path(r'^app/(?P<app_id>[\w-]+)/cas/proxy/$', ProxyView.as_view(), name='cas_proxy'),
    re_path(r'^app/(?P<app_id>[\w-]+)/cas/p3/serviceValidate/$', ServiceValidateView.as_view(), name='cas_p3_service_validate'),
    re_path(r'^app/(?P<app_id>[\w-]+)/cas/p3/proxyValidate/$', ProxyValidateView.as_view(), name='cas_p3_proxy_validate'),
    re_path(r'^app/(?P<app_id>[\w-]+)/cas/warn/$', WarnView.as_view(), name='cas_warn'),
    re_path(r'^app/(?P<app_id>[\w-]+)/cas/samlValidate/$', SamlValidateView.as_view(), name='cas_saml_validate'),
]
