from .base import BaseViewSet
from rest_framework import viewsets
from common.extension import InMemExtension
from extension.utils import find_installed_extensions
from api.v1.serializers.extension import ExtensionSerializer, ExtensionListSerializer
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, PolymorphicProxySerializer
from extension.models import Extension
from runtime import get_app_runtime


ExtensionPolymorphicProxySerializer = PolymorphicProxySerializer(
    component_name='ExtensionPolymorphicProxySerializer',
    serializers=get_app_runtime().extension_serializers,
    resource_type_field_name='type'
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
        responses=ExtensionListSerializer
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        request=ExtensionPolymorphicProxySerializer,
        responses=ExtensionPolymorphicProxySerializer,
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        request=ExtensionPolymorphicProxySerializer,
        responses=ExtensionPolymorphicProxySerializer,
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        responses=ExtensionPolymorphicProxySerializer
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
