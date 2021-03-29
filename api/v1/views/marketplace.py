from .base import BaseViewSet
from rest_framework import viewsets
from common.extension import InMemExtension
from extension.utils import find_installed_extensions
from api.v1.serializers.market_extension import MarketPlaceExtensionSerializer
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema

@extend_schema(tags = ['market-extension'])
class MarketPlaceViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = MarketPlaceExtensionSerializer

    def get_queryset(self):
        extensions = find_installed_extensions()
        print(extensions)
        return extensions

    def get_object(self):
        ext: InMemExtension
        extensions = find_installed_extensions()
        for ext in extensions:
            if ext.name == self.kwargs['pk']:
                return ext

        return None
