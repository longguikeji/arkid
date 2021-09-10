from django.http import Http404
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated

from api.v1.serializers.permission import (
    PermissionSerializer, PermissionCreateSerializer
)
from tenant.models import (
    Tenant,
)
from common.paginator import DefaultListPaginator
from openapi.utils import extend_schema
from .base import BaseTenantViewSet
from inventory.models import Permission
from rest_framework import viewsets
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication


@extend_schema(
    roles=['tenant admin', 'global admin'],
    tags = ['permission']
)
class PermissionViewSet(BaseTenantViewSet, viewsets.ReadOnlyModelViewSet):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = PermissionSerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        context = self.get_serializer_context()
        tenant = context['tenant']

        objs = Permission.objects.filter(
            is_system_permission=True,
            tenant=tenant,
        )

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
    tags = ['permission']
)
class PermissionCreateView(generics.CreateAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = PermissionCreateSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['tenant'] = Tenant.objects.filter(uuid=self.kwargs['tenant_uuid']).first()
        return context