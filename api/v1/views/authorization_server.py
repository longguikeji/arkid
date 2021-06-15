from authorization_server.models import AuthorizationServer
from rest_framework import viewsets
from api.v1.serializers.authorization_server import AuthorizationServerSerializer
from rest_framework.decorators import action
from runtime import get_app_runtime
from openapi.utils import extend_schema
from common.paginator import DefaultListPaginator


@extend_schema(
    roles=['tenant admin', 'global admin'], tags = ['authorizationServer']
)
class AuthorizationServerViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = AuthorizationServerSerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        runtime = get_app_runtime()
        objs = runtime.authorization_servers
        return objs

    def get_object(self):
        runtime = get_app_runtime()

        obj: AuthorizationServer
        objs = runtime.authorization_servers
        for obj in objs:
            if obj.id == self.kwargs['pk']:
                return obj

        return None
        
