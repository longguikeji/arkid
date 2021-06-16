from .base import BaseViewSet
from rest_framework import viewsets
from common.extension import InMemExtension
from extension.utils import find_available_extensions
from api.v1.serializers.market_extension import MarketPlaceExtensionSerializer, MarketPlaceExtensionTagsSerializer
from rest_framework.decorators import action
from openapi.utils import extend_schema
from rest_framework import generics
from django.http.response import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication


@extend_schema(roles=['tenant admin', 'global admin'], tags=['market-extension'])
class MarketPlaceViewSet(viewsets.ReadOnlyModelViewSet):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

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
                    tags_cp = tags.split(',')
                    extension_type_cp = extension_type.split(',')
                    scope_cp = scope.split(',')
                    if tags_cp and extension.tags in tags_cp and extension_type_cp and extension.type in extension_type_cp and scope_cp and extension.scope in scope_cp:
                        result.append(extension)
                elif tags and extension_type:
                    tags_cp = tags.split(',')
                    extension_type_cp = extension_type.split(',')
                    if tags_cp and extension.tags in tags_cp and extension_type_cp and extension.type in extension_type_cp:
                        result.append(extension)
                elif tags and scope:
                    tags_cp = tags.split(',')
                    scope_cp = scope.split(',')
                    if tags_cp and extension.tags in tags_cp and scope_cp and extension.scope in scope_cp:
                        result.append(extension)
                elif tags:
                    tags_cp = tags.split(',')
                    if tags_cp and extension.tags in tags_cp:
                        result.append(extension)
                elif scope:
                    scope_cp = scope.split(',')
                    if scope_cp and extension.scope in scope_cp:
                        result.append(extension)
                elif extension_type:
                    extension_type_cp = extension_type.split(',')
                    if extension_type_cp and extension.type in extension_type_cp:
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


@extend_schema(roles=['tenant admin', 'global admin'], tags=['market-extension'])
class MarketPlaceTagsViewSet(generics.RetrieveAPIView):

    serializer_class = MarketPlaceExtensionTagsSerializer

    def get(self, request):
        extensions = find_available_extensions()
        tags = []
        for extension in extensions:
            tags.append(extension.tags)
        tags = list(set(tags))
        return JsonResponse({"data": tags})
