from django.http import Http404
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from .base import BaseViewSet

from app.models import App
from api.v1.serializers.app import (
    AppSerializer,
    AppListSerializer,
    AppProvisioningSerializer,
)
from common.paginator import DefaultListPaginator
from drf_spectacular.utils import extend_schema, PolymorphicProxySerializer
from runtime import get_app_runtime
from provisioning.models import Config

AppPolymorphicProxySerializer = PolymorphicProxySerializer(
    component_name='AppPolymorphicProxySerializer',
    serializers=get_app_runtime().app_type_serializers,
    resource_type_field_name='type',
)


@extend_schema(
    tags=['app'],
)
class AppViewSet(BaseViewSet):

    permission_classes = []
    authentication_classes = []

    serializer_class = AppSerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        context = self.get_serializer_context()
        tenant = context['tenant']
        qs = App.active_objects.filter(tenant=tenant).order_by('id')
        return qs

    def get_object(self):
        uuid = self.kwargs['pk']
        context = self.get_serializer_context()
        tenant = context['tenant']

        return (
            App.active_objects.filter(
                tenant=tenant,
                uuid=uuid,
            )
            .order_by('id')
            .first()
        )

    @extend_schema(responses=AppListSerializer)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        request=AppPolymorphicProxySerializer,
        responses=AppPolymorphicProxySerializer,
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        request=AppPolymorphicProxySerializer,
        responses=AppPolymorphicProxySerializer,
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(responses=AppPolymorphicProxySerializer)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


@extend_schema(tags=['app'])
class AppProvisioningViewSet(BaseViewSet):

    # permission_classes = [IsAuthenticated]
    # authentication_classes = [ExpiringTokenAuthentication]

    model = Config

    permission_classes = []
    authentication_classes = []

    serializer_class = AppProvisioningSerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        context = self.get_serializer_context()
        tenant = context['tenant']
        app = context['app']
        all_configs = Config.active_objects.filter(
            app=app,
        )
        return all_configs
