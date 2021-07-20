from django.conf.urls import url
from mama_cas import views


urlpatterns = [
    url(r'cas/login/?$', views.LoginView.as_view(), name='cas_login'),
    # url(r'cas/logout/?$', views.LogoutView.as_view(), name='cas_logout'),
    # url(r'cas/validate/?$', views.ValidateView.as_view(), name='cas_validate'),
    url(r'cas/validate/?$', views.ServiceValidateView.as_view(),
        name='cas_service_validate'),
    # url(r'cas/proxyValidate/?$', views.ProxyValidateView.as_view(),
    #     name='cas_proxy_validate'),
    # url(r'cas/proxy/?$', views.ProxyView.as_view(), name='cas_proxy'),
    # url(r'cas/p3/serviceValidate/?$', views.ServiceValidateView.as_view(),
    #     name='cas_p3_service_validate'),
    # url(r'cas/p3/proxyValidate/?$', views.ProxyValidateView.as_view(),
    #     name='cas_p3_proxy_validate'),
    # url(r'cas/warn/?$', views.WarnView.as_view(), name='cas_warn'),
    # url(r'cas/samlValidate/?$', views.SamlValidateView.as_view(),
    #     name='cas_saml_validate'),
]
