from django.urls import re_path

from api.v1.views import bind_saas


urlpatterns = [
    re_path(
        r'^tenant/(?P<tenant_uuid>[\w-]+)/bind_saas/',
        bind_saas.ArkIDBindSaasAPIView.as_view(),
        name='statistics',
    ),
]
