from .base import BaseViewSet
from rest_framework import viewsets
from extension.models import Extension
from extension.utils import find_installed_extensions
from api.v1.serializers.extension import ExtensionSerializer
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema

@extend_schema(tags = ['extension'])
class ExtensionViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = ExtensionSerializer

    def get_queryset(self):
        extensions = find_installed_extensions()
        return extensions

    def get_object(self):
        ext: Extension
        extensions = find_installed_extensions()
        for ext in extensions:
            if ext.name == self.kwargs['pk']:
                return ext

        return None

    # @action(detail=True, methods=['get', 'post'])
    # def test(self, request, parent_lookup_tenant, pk):
    #     xx
