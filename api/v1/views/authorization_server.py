from authorization_server.models import AuthorizationServer
from rest_framework import viewsets
from api.v1.serializers.authorization_server import AuthorizationServerSerializer
from rest_framework.decorators import action
from runtime import get_app_runtime
from openapi.utils import extend_schema
from common.paginator import DefaultListPaginator
from tenant.models import (
    Tenant,
)

@extend_schema(
    roles=['tenantadmin', 'globaladmin'], tags = ['authorizationServer']
)
class AuthorizationServerViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = AuthorizationServerSerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        context = self.get_serializer_context()
        tenant = context['tenant']
        user = self.request.user
        check_result = user.check_permission(tenant)
        if not check_result is None:
            return []

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
        
