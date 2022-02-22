from .base import BaseViewSet
from api.v1.serializers.extension import ExtensionSerializer, ExtensionListSerializer
from openapi.utils import extend_schema
from drf_spectacular.utils import PolymorphicProxySerializer
from extension.models import Extension
from runtime import get_app_runtime
from django.http.response import JsonResponse
from drf_spectacular.utils import extend_schema_view
from rest_framework.permissions import IsAuthenticated
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from django.utils.translation import gettext_lazy as _
from extension.utils import reload_extension
from common.code import Code


serializers = get_app_runtime().extension_serializers
ExtensionPolymorphicProxySerializer = PolymorphicProxySerializer(
    component_name='ExtensionPolymorphicProxySerializer',
    serializers=serializers,
    resource_type_field_name='type'
)

type_serializers = {name: ExtensionListSerializer for name in serializers}
ExtensionTypePolymorphicProxySerializer = PolymorphicProxySerializer(
    component_name='ExtensionTypePolymorphicProxySerializer',
    serializers=type_serializers,
    resource_type_field_name='type'
)

@extend_schema_view(
    destroy=extend_schema(roles=['globaladmin']),
    partial_update=extend_schema(roles=['globaladmin']),
)
@extend_schema(tags = ['extension'])
class ExtensionViewSet(BaseViewSet):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]
    serializer_class = ExtensionSerializer
    serializer_action_classes = {
        'create': ExtensionListSerializer,
    }

    def get_serializer_class(self):
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return super().get_serializer_class()

    def get_queryset(self):
        return Extension.valid_objects.filter()

    def get_object(self):
        o = Extension.valid_objects.filter(
            uuid=self.kwargs['pk']
        ).first()

        return o

    @extend_schema(
        roles=['globaladmin'],
        responses=ExtensionListSerializer
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        roles=['globaladmin'],
        request=ExtensionPolymorphicProxySerializer,
        responses=ExtensionPolymorphicProxySerializer,
    )
    def update(self, request, *args, **kwargs):
        data = request.data.get('data', {})
        data_path = data.get('data_path', '')
        if data_path:
            if '../' in data_path or './' in data_path:
                return JsonResponse(data={
                    'error': Code.DATA_PATH_ERROR.value,
                    'message': _('data_path format error'),
                })
        return super().update(request, *args, **kwargs)

    @extend_schema(
        roles=['globaladmin'],
        request=ExtensionTypePolymorphicProxySerializer,
        responses=ExtensionTypePolymorphicProxySerializer,
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        roles=['globaladmin'],
        responses=ExtensionPolymorphicProxySerializer
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        roles=['globaladmin'],
    )
    def destroy(self, request, *args, **kwargs):
        o = self.get_object()
        result = super(ExtensionViewSet, self).destroy(request, *args, **kwargs)
        reload_extension(o.type, False)
        return result