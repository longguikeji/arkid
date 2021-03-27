from django.urls import path, include

from api.v1.views import (
    extension as views_extension
)

from .tenant import tenant_router


tenant_oauth_authorization_server_router = tenant_router.register(r'extension', views_extension.ExtensionViewSet, basename='tenant-extension', parents_query_lookups=['tenant'])

urlpatterns = [
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
]