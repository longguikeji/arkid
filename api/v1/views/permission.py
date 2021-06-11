from django.http import Http404
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated

from api.v1.serializers.permission import (
    PermissionSerializer
)
from common.paginator import DefaultListPaginator
from openapi.utils import extend_schema
from .base import BaseTenantViewSet
from inventory.models import Permission
from rest_framework import viewsets


@extend_schema(
    roles=['general user', 'tenant admin', 'global admin'],
    tags = ['permission']
)
class PermissionViewSet(BaseTenantViewSet, viewsets.ReadOnlyModelViewSet):

    # permission_classes = [IsAuthenticated]
    # authentication_classes = [ExpiringTokenAuthentication]

    permission_classes = []
    authentication_classes = []

    serializer_class = PermissionSerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        context = self.get_serializer_context()
        tenant = context['tenant']

        objs = Permission.objects.filter(
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