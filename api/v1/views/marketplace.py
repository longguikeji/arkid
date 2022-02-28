from .base import BaseViewSet
from rest_framework import viewsets
from common.paginator import DefaultListPaginator
from common.extension import InMemExtension
from extension.models import Extension
from extension.utils import find_available_extensions
from api.v1.serializers.market_extension import MarketPlaceExtensionSerializer, MarketPlaceExtensionTagsSerializer
from rest_framework.decorators import action
from openapi.utils import extend_schema
from drf_spectacular.utils import OpenApiParameter
from perm.custom_access import ApiAccessPermission
from rest_framework import generics
from django.http.response import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication


@extend_schema(
    roles=['globaladmin'],
    tags=['market-extension'],
)
class MarketPlaceViewSet(viewsets.ReadOnlyModelViewSet):

    permission_classes = [IsAuthenticated, ApiAccessPermission]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = MarketPlaceExtensionSerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        tags = self.request.query_params.get('tags', '')
        extension_type = self.request.query_params.get('type', '')
        scope = self.request.query_params.get('scope', '')
        installed = self.request.query_params.get('installed', '')
        enabled = self.request.query_params.get('enabled', '')

        extensions = find_available_extensions()
        installed_extensions = Extension.valid_objects.filter()
        installed_extensions_dict = {ext.type: ext for ext in installed_extensions}
        for extension in extensions:
            ext = installed_extensions_dict.get(extension.name)
            if ext:
                extension.uuid = ext.uuid
                extension.installed = '已安装'
                extension.enabled = '已启用' if ext.is_active else '未启用'
            else:
                extension.uuid = ''
                extension.installed = '未安装'
                extension.enabled = '未启用'

        if tags or extension_type or scope or installed or enabled:
            result = []
            for extension in extensions:
                if tags:
                    tags_list = tags.split(',')
                    if extension.tags not in tags_list:
                        continue
                if extension_type:
                    extension_type_list = extension_type.split(',')
                    if extension.type not in extension_type_list:
                        continue
                if scope:
                    scope_list = scope.split(',')
                    if extension.scope not in scope_list:
                        continue
                if installed:
                    installed_list = installed.split(',')
                    if extension.installed not in installed_list:
                        continue
                if enabled:
                    enabled_list = enabled.split(',')
                    if extension.enabled not in enabled_list:
                        continue
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


    @extend_schema(
        roles=['globaladmin'],
        summary='插件市场列表',
        parameters=[
            OpenApiParameter(
                name='tags',
                type={'type': 'string'},
                location=OpenApiParameter.QUERY,
                required=False,
            ),
            OpenApiParameter(
                name='type',
                type={'type': 'string'},
                location=OpenApiParameter.QUERY,
                required=False,
            ),
            OpenApiParameter(
                name='scope',
                type={'type': 'string'},
                location=OpenApiParameter.QUERY,
                required=False,
            ),
            OpenApiParameter(
                name='installed',
                type={'type': 'string'},
                enum=['已安装','未安装'],
                location=OpenApiParameter.QUERY,
                description='是否已安装',
                required=False,
            ),
            OpenApiParameter(
                name='enabled',
                type={'type': 'string'},
                enum=['已启用','未启用'],
                location=OpenApiParameter.QUERY,
                description='是否已启用',
                required=False,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        roles=['globaladmin'],
        summary='插件市场插件详情'
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

@extend_schema(roles=['globaladmin'], tags=['market-extension'], summary='插件市场标签')
class MarketPlaceTagsViewSet(generics.RetrieveAPIView):

    serializer_class = MarketPlaceExtensionTagsSerializer

    def get(self, request):
        extensions = find_available_extensions()
        tags = []
        for extension in extensions:
            tags.append(extension.tags)
        tags = list(set(tags))
        return JsonResponse({"data": tags})
