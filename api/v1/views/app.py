from django.http import Http404
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from .base import BaseViewSet
from common.code import Code
from rest_framework.response import Response

from app.models import (
    App
)
from api.v1.serializers.app import (
    AppSerializer, AppListSerializer, AddAuthTmplSerializer
)
from common.paginator import DefaultListPaginator
from drf_spectacular.utils import extend_schema, PolymorphicProxySerializer
from runtime import get_app_runtime
from rest_framework.decorators import action
from oauth2_provider.models import Application

AppPolymorphicProxySerializer = PolymorphicProxySerializer(
    component_name='AppPolymorphicProxySerializer',
    serializers=get_app_runtime().app_type_serializers,
    resource_type_field_name='type'
)


@extend_schema(
    tags = ['app'],
)
class AppViewSet(BaseViewSet):

    permission_classes = []
    authentication_classes = []

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
        responses=AppListSerializer
    )
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

    @extend_schema(
        responses=AppPolymorphicProxySerializer
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


    @extend_schema(
        request=AddAuthTmplSerializer,
        responses=AddAuthTmplSerializer,
    )
    @action(detail=True, methods=['post'])
    def add_auth_tmpl(self, request, *args, **kwargs):
        context = self.get_serializer_context()
        tenant = context['tenant']
        app_uuid = self.kwargs['pk']
        app = App.active_objects.filter(tenant=tenant, uuid=app_uuid).first()
        tmpl = request.data.get('html')

        if not app:
            return {
                'error': Code.ADD_AUTH_TMPL_ERROR,
                'message': 'No app found'
            }
        app.auth_tmpl = tmpl
        app.save()

        auth_app = Application.objects.filter(name=app.id).first()
        if not auth_app:
            return {
                'error': Code.ADD_AUTH_TMPL_ERROR,
                'message': 'No oauth app found'
            }
        auth_app.custom_template = tmpl
        auth_app.save()
        return Response({
            'error': Code.OK.value
        })
