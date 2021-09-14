from django.http import Http404
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated

from api.v1.serializers.permission import (
    PermissionSerializer, PermissionCreateSerializer, PermissionGroupListSerializer,
    PermissionGroupCreateSerializer,
)
from tenant.models import (
    Tenant,
)
from common.paginator import DefaultListPaginator
from openapi.utils import extend_schema
from .base import BaseTenantViewSet
from inventory.models import Permission, PermissionGroup
from rest_framework import viewsets
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication


@extend_schema(
    roles=['tenant admin', 'global admin'],
    tags=['permission']
)
class PermissionViewSet(BaseTenantViewSet, viewsets.ReadOnlyModelViewSet):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = PermissionSerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        context = self.get_serializer_context()
        tenant = context['tenant']

        objs = Permission.valid_objects.filter(
            tenant=tenant,
        ).order_by('id')

        return objs

    def get_object(self):
        context = self.get_serializer_context()
        tenant = context['tenant']

        kwargs = {
            'tenant': tenant,
            'uuid': self.kwargs['pk'],
        }

        obj = Permission.valid_objects.filter(**kwargs).first()
        return obj


@extend_schema(
    roles=['tenant admin', 'global admin'],
    tags=['permission']
)
class PermissionCreateView(generics.CreateAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = PermissionCreateSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['tenant'] = Tenant.objects.filter(uuid=self.kwargs['tenant_uuid']).first()
        return context


@extend_schema(
    roles=['tenant admin', 'global admin'],
    tags=['permission']
)
class PermissionView(generics.RetrieveUpdateDestroyAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = PermissionCreateSerializer

    def get_object(self):
        tenant_uuid = self.kwargs['tenant_uuid']
        kwargs = {
            'tenant__uuid': tenant_uuid,
            'uuid': self.kwargs['permission_uuid'],
        }

        obj = Permission.valid_objects.filter(**kwargs).first()
        return obj

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['tenant'] = Tenant.objects.filter(uuid=self.kwargs['tenant_uuid']).first()
        return context


@extend_schema(
    roles=['tenant admin', 'global admin'],
    tags=['permission']
)
class PermissionGroupView(generics.ListAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = PermissionGroupListSerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        tenant_uuid = self.kwargs['tenant_uuid']
        kwargs = {
            'tenant__uuid': tenant_uuid,
        }
        permission_groups = PermissionGroup.valid_objects.filter(**kwargs).order_by('-id')
        return permission_groups


@extend_schema(
    roles=['tenant admin', 'global admin'],
    tags=['permission']
)
class PermissionGroupCreateView(generics.CreateAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = PermissionGroupCreateSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['tenant'] = Tenant.objects.filter(uuid=self.kwargs['tenant_uuid']).first()
        return context


@extend_schema(
    roles=['tenant admin', 'global admin'],
    tags=['permission']
)
class PermissionGroupDetailView(generics.RetrieveUpdateDestroyAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = PermissionGroupCreateSerializer

    def get_object(self):
        tenant_uuid = self.kwargs['tenant_uuid']
        kwargs = {
            'tenant__uuid': tenant_uuid,
            'uuid': self.kwargs['permission_group_uuid'],
        }

        obj = PermissionGroup.valid_objects.filter(**kwargs).first()
        return obj

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['tenant'] = Tenant.objects.filter(uuid=self.kwargs['tenant_uuid']).first()
        return context
