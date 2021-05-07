from .base import BaseViewSet
from rest_framework import viewsets
from common.extension import InMemExtension
from extension.utils import find_available_extensions
from api.v1.serializers.market_extension import MarketPlaceExtensionSerializer, MarketPlaceExtensionTagsSerializer
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema
from rest_framework import generics
from django.http.response import JsonResponse


@extend_schema(tags=['market-extension'])
class MarketPlaceViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = MarketPlaceExtensionSerializer

    def get_queryset(self):
        tags = self.request.query_params.get('tags', '')
        extension_type = self.request.query_params.get('type', '')
        scope = self.request.query_params.get('scope', '')
        extensions = find_available_extensions()
        if tags or extension_type or scope:
            result = []
            for extension in extensions:
                if tags and extension_type and scope:
                    if tags and tags in extension.tags and extension_type and extension_type in extension.type and scope and scope in extension.scope:
                        result.append(extension)
                elif tags and extension_type:
                    if tags and tags in extension.tags and extension_type and extension_type in extension.type:
                        result.append(extension)
                elif tags and scope:
                    if tags and tags in extension.tags or scope and scope in extension.scope:
                        result.append(extension)
                elif tags:
                    if tags and tags in extension.tags:
                        result.append(extension)
                elif scope:
                    if scope and scope in extension.scope:
                        result.append(extension)
                elif extension_type:
                    if extension_type and extension_type in extension.type:
                        result.append(extension)
            extensions = result
        return extensions

    def get_object(self):
        ext: InMemExtension
        extensions = find_available_extensions()
        for ext in extensions:
            if ext.name == self.kwargs['pk']:
                return ext

        return None


@extend_schema(tags=['market-extension'])
class MarketPlaceTagsViewSet(generics.RetrieveAPIView):

    serializer_class = MarketPlaceExtensionTagsSerializer

    def get(self, request):
        extensions = find_available_extensions()
        tags = []
        for extension in extensions:
            tags.append(extension.tags)
        tags = list(set(tags))
        return JsonResponse({"data": tags})
