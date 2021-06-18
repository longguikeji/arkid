
from .base import BaseViewSet

from app.models import (
    App
)
from api.v1.serializers.app import (
    AppSerializer, AppListSerializer
)
from common.paginator import DefaultListPaginator
from django.http.response import JsonResponse
from openapi.utils import extend_schema
from drf_spectacular.utils import PolymorphicProxySerializer
from runtime import get_app_runtime
from drf_spectacular.utils import extend_schema_view
from rest_framework.permissions import IsAuthenticated
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from django.utils.translation import gettext_lazy as _
from common.code import Code

AppPolymorphicProxySerializer = PolymorphicProxySerializer(
    component_name='AppPolymorphicProxySerializer',
    serializers=get_app_runtime().app_type_serializers,
    resource_type_field_name='type'
)

@extend_schema_view(
    destroy=extend_schema(roles=['tenant admin', 'global admin']),
    partial_update=extend_schema(roles=['tenant admin', 'global admin']),
)
@extend_schema(
    tags = ['app'],
)
class AppViewSet(BaseViewSet):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = AppSerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        context = self.get_serializer_context()
        tenant = context['tenant']
        qs = App.active_objects.filter(
            tenant=tenant
        ).order_by('id')
        return qs
    
    def get_object(self):
        uuid = self.kwargs['pk']
        context = self.get_serializer_context()
        tenant = context['tenant']
        
        return App.active_objects.filter(
            tenant=tenant,
            uuid=uuid,
        ).order_by('id').first()

    @extend_schema(
        roles=['tenant admin', 'global admin'],
        responses=AppListSerializer
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        roles=['tenant admin', 'global admin'],
        request=AppPolymorphicProxySerializer,
        responses=AppPolymorphicProxySerializer,
    )
    def update(self, request, *args, **kwargs):
        data = request.data.get('data','')
        if data:
            redirect_uris = data.get('redirect_uris', '')
            if redirect_uris:
                if redirect_uris.startswith('http') or redirect_uris.startswith('https'):
                    pass
                else:
                    return JsonResponse(data={
                        'error': Code.URI_FROMAT_ERROR.value,
                        'message': _('redirect_uris format error'),
                    })
        return super().update(request, *args, **kwargs)

    @extend_schema(
        roles=['tenant admin', 'global admin'],
        request=AppPolymorphicProxySerializer,
        responses=AppPolymorphicProxySerializer,
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        roles=['tenant admin', 'global admin'],
        responses=AppPolymorphicProxySerializer
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
