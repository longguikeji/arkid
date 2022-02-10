from django.urls import re_path

from api.v1.views import arkstore


urlpatterns = [
    re_path(
        r'^tenant/(?P<tenant_uuid>[\w-]+)/arkstore/$',
        arkstore.ArkStoreAPIView.as_view(),
        name='arkstore',
    ),
    re_path(
        r'^tenant/(?P<tenant_uuid>[\w-]+)/arkstore/download/(?P<pk>[\w-]+)/$',
        arkstore.ArkStoreDownloadView.as_view(),
        name='arkstore',
    ),
    re_path(
        r'^tenant/(?P<tenant_uuid>[\w-]+)/arkstore/order/$',
        arkstore.ArkStoreOrderView.as_view(),
        name='arkstore',
    ),
]
