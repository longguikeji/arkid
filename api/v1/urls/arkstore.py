from django.urls import re_path

from api.v1.views import arkstore


urlpatterns = [
    re_path(
        r'^tenant/(?P<tenant_uuid>[\w-]+)/arkstore/$',
        arkstore.ArkStoreAPIView.as_view(),
        name='arkstore',
    ),
    re_path(
        r'^tenant/(?P<tenant_uuid>[\w-]+)/arkstore/install/(?P<pk>[\w-]+)/$',
        arkstore.ArkStoreInstallView.as_view(),
        name='arkstore',
    ),
    re_path(
        r'^tenant/(?P<tenant_uuid>[\w-]+)/arkstore/order/$',
        arkstore.ArkStoreOrderView.as_view(),
        name='arkstore',
    ),
    re_path(
        r'^tenant/(?P<tenant_uuid>[\w-]+)/arkstore/bind_agent/$',
        arkstore.ArkStoreBindAgentView.as_view(),
        name='arkstore',
    ),
    re_path(
        r'^tenant/(?P<tenant_uuid>[\w-]+)/arkstore/auto_fill_form/(?P<pk>[\w-]+)/$',
        arkstore.ArkStoreGetAutoFormFillDataView.as_view(),
        name='arkstore',
    ),
]
