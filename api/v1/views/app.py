from .base import BaseViewSet
from common.code import Code
from rest_framework.response import Response

from app.models import App
from api.v1.serializers.app import (
    AppSerializer,
    AppListSerializer,
    AppProvisioningSerializer,
    AppProvisioningMappingSerializer,
    AppProvisioningProfileSerializer,
    AddAuthTmplSerializer,
)
from common.paginator import DefaultListPaginator
from django.http.response import JsonResponse
from openapi.utils import extend_schema
from drf_spectacular.utils import PolymorphicProxySerializer
from runtime import get_app_runtime
from provisioning.models import Config
from schema.models import Schema, AppProfile
from rest_framework.decorators import action
from oauth2_provider.models import Application
from drf_spectacular.utils import extend_schema_view
from rest_framework.permissions import IsAuthenticated
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from django.utils.translation import gettext_lazy as _
from common.code import Code
from webhook.manager import WebhookManager
from django.db import transaction


AppPolymorphicProxySerializer = PolymorphicProxySerializer(
    component_name='AppPolymorphicProxySerializer',
    serializers=get_app_runtime().app_type_serializers,
    resource_type_field_name='type',
)


@extend_schema_view(
    destroy=extend_schema(roles=['tenant admin', 'global admin']),
    partial_update=extend_schema(roles=['tenant admin', 'global admin']),
)
@extend_schema(
    tags=['app'],
)
class AppViewSet(BaseViewSet):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

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

    @extend_schema(
        roles=['tenant admin', 'global admin'],
    )
    @transaction.atomic()
    def destroy(self, request, *args, **kwargs):
        context = self.get_serializer_context()
        tenant = context['tenant']
        app = self.get_object()
        ret = super().destroy(request, *args, **kwargs)
        transaction.on_commit(lambda: WebhookManager.app_deleted(tenant.uuid, app))
        return ret

    @extend_schema(roles=['tenant admin', 'global admin'], responses=AppListSerializer)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        roles=['tenant admin', 'global admin'],
        request=AppPolymorphicProxySerializer,
        responses=AppPolymorphicProxySerializer,
    )
    def update(self, request, *args, **kwargs):
        data = request.data.get('data', '')
        if data:
            redirect_uris = data.get('redirect_uris', '')
            if redirect_uris:
                if redirect_uris.startswith('http') or redirect_uris.startswith(
                    'https'
                ):
                    pass
                else:
                    return JsonResponse(
                        data={
                            'error': Code.URI_FROMAT_ERROR.value,
                            'message': _('redirect_uris format error'),
                        }
                    )
        return super().update(request, *args, **kwargs)

    @extend_schema(
        roles=['tenant admin', 'global admin'],
        request=AppPolymorphicProxySerializer,
        responses=AppPolymorphicProxySerializer,
    )
    def create(self, request, *args, **kwargs):
        data = request.data.get('data', '')
        if data:
            redirect_uris = data.get('redirect_uris', '')
            if redirect_uris:
                if redirect_uris.startswith('http') or redirect_uris.startswith(
                    'https'
                ):
                    pass
                else:
                    return JsonResponse(
                        data={
                            'error': Code.URI_FROMAT_ERROR.value,
                            'message': _('redirect_uris format error'),
                        }
                    )
        return super().create(request, *args, **kwargs)

    @extend_schema(
        roles=['tenant admin', 'global admin'], responses=AppPolymorphicProxySerializer
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
            return {'error': Code.ADD_AUTH_TMPL_ERROR, 'message': 'No app found'}
        app.auth_tmpl = tmpl
        app.save()

        auth_app = Application.objects.filter(name=app.id).first()
        if not auth_app:
            return {'error': Code.ADD_AUTH_TMPL_ERROR, 'message': 'No oauth app found'}
        auth_app.custom_template = tmpl
        auth_app.save()
        return Response({'error': Code.OK.value})


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


@extend_schema(tags=['app'])
class AppProvisioningMappingViewSet(BaseViewSet):

    # permission_classes = [IsAuthenticated]
    # authentication_classes = [ExpiringTokenAuthentication]

    model = Schema

    permission_classes = []
    authentication_classes = []

    serializer_class = AppProvisioningMappingSerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        context = self.get_serializer_context()
        tenant = context['tenant']
        app = context['app']
        provisioning = context.get('provisioning')
        mapping = Schema.active_objects.filter(
            provisioning_config=provisioning,
        )
        return mapping


@extend_schema(tags=['app'])
class AppProvisioningProfileViewSet(BaseViewSet):

    # permission_classes = [IsAuthenticated]
    # authentication_classes = [ExpiringTokenAuthentication]

    model = AppProfile

    permission_classes = []
    authentication_classes = []

    serializer_class = AppProvisioningProfileSerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        context = self.get_serializer_context()
        tenant = context['tenant']
        app = context['app']
        provisioning = context.get('provisioning')
        mapping = AppProfile.active_objects.filter(
            provisioning_config=provisioning,
        )
        return mapping
