"""
(2) CAS server URIs as described in the CAS protocol.
"""

from django.urls import re_path

from mama_cas.views import LoginView
from mama_cas.views import LogoutView
from mama_cas.views import ValidateView
from mama_cas.views import ServiceValidateView
from mama_cas.views import ProxyValidateView
from mama_cas.views import ProxyView
from mama_cas.views import WarnView
from mama_cas.views import SamlValidateView


urlpatterns = [
    re_path(r'^login/?$', LoginView.as_view(), name='cas_login'),
    re_path(r'^logout/?$', LogoutView.as_view(), name='cas_logout'),
    re_path(r'^validate/?$', ValidateView.as_view(), name='cas_validate'),
    re_path(r'^serviceValidate/?$', ServiceValidateView.as_view(), name='cas_service_validate'),
    re_path(r'^proxyValidate/?$', ProxyValidateView.as_view(), name='cas_proxy_validate'),
    re_path(r'^proxy/?$', ProxyView.as_view(), name='cas_proxy'),
    re_path(r'^p3/serviceValidate/?$', ServiceValidateView.as_view(), name='cas_p3_service_validate'),
    re_path(r'^p3/proxyValidate/?$', ProxyValidateView.as_view(), name='cas_p3_proxy_validate'),
    re_path(r'^warn/?$', WarnView.as_view(), name='cas_warn'),
    re_path(r'^samlValidate/?$', SamlValidateView.as_view(), name='cas_saml_validate'),
]
