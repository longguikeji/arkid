from authorization_server.models import AuthorizationServer
from rest_framework import viewsets
from api.v1.serializers.authorization_server import AuthorizationServerSerializer
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from rest_framework.decorators import action
from runtime import get_app_runtime
from openapi.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from perm.custom_access import ApiAccessPermission
from common.paginator import DefaultListPaginator
from tenant.models import (
    Tenant,
)

@extend_schema(
    roles=['tenantadmin', 'globaladmin', 'linkidentity.identityservice'], tags = ['authorizationServer'], summary='认证服务'
)
class AuthorizationServerViewSet(viewsets.ReadOnlyModelViewSet):

    permission_classes = [IsAuthenticated, ApiAccessPermission]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = AuthorizationServerSerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        runtime = get_app_runtime()
        objs = runtime.authorization_servers
        return objs

    def get_serializer_context(self):
        context = super().get_serializer_context()
        from rest_framework_extensions.settings import extensions_api_settings
        context['tenant'] = Tenant.objects.filter(uuid=self.kwargs[extensions_api_settings.DEFAULT_PARENT_LOOKUP_KWARG_NAME_PREFIX + 'tenant']).first()
        return context

    def get_object(self):
        runtime = get_app_runtime()

        obj: AuthorizationServer
        objs = runtime.authorization_servers
        for obj in objs:
            if obj.id == self.kwargs['pk']:
                return obj

        return None
        