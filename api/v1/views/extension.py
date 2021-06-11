from .base import BaseViewSet
from api.v1.serializers.extension import ExtensionSerializer, ExtensionListSerializer
from openapi.utils import extend_schema
from drf_spectacular.utils import PolymorphicProxySerializer
from extension.models import Extension
from runtime import get_app_runtime
from drf_spectacular.utils import extend_schema_view


ExtensionPolymorphicProxySerializer = PolymorphicProxySerializer(
    component_name='ExtensionPolymorphicProxySerializer',
    serializers=get_app_runtime().extension_serializers,
    resource_type_field_name='type'
)

@extend_schema_view(
    destroy=extend_schema(roles=['tenant admin', 'global admin']),
    partial_update=extend_schema(roles=['tenant admin', 'global admin']),
)
@extend_schema(tags = ['extension'])
class ExtensionViewSet(BaseViewSet):

    serializer_class = ExtensionSerializer

    def get_queryset(self):
        return Extension.valid_objects.filter()

    def get_object(self):
        o = Extension.valid_objects.filter(
            uuid=self.kwargs['pk']
        ).first()

        return o

    @extend_schema(
        roles=['tenant admin', 'global admin'],
        responses=ExtensionListSerializer
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        roles=['tenant admin', 'global admin'],
        request=ExtensionPolymorphicProxySerializer,
        responses=ExtensionPolymorphicProxySerializer,
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        roles=['tenant admin', 'global admin'],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        roles=['tenant admin', 'global admin'],
        request=ExtensionPolymorphicProxySerializer,
        responses=ExtensionPolymorphicProxySerializer,
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        roles=['tenant admin', 'global admin'],
        responses=ExtensionPolymorphicProxySerializer
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
