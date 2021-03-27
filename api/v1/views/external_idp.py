from rest_framework.fields import JSONField
from external_idp.models import ExternalIdp
import runtime
from .base import BaseViewSet
from rest_framework import viewsets
from extension.models import Extension
from api.v1.serializers.external_idp import ExternalIdpSerializer
from rest_framework.decorators import action
from runtime import get_app_runtime
from django.http.response import JsonResponse
from drf_spectacular.utils import extend_schema
from common.paginator import DefaultListPaginator

@extend_schema(
    tags = ['externalIdp']
)
class ExternalIdpViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = ExternalIdpSerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        runtime = get_app_runtime()
        objs = runtime.external_idps
        return objs

    def get_object(self):
        runtime = get_app_runtime()

        obj: ExternalIdp
        objs = runtime.external_idps
        for obj in objs:
            if obj.name == self.kwargs['pk']:
                return obj

        return None

    @action(detail=True, methods=['get'])
    def manual_import(self, request, parent_lookup_tenant, pk):
        runtime = get_app_runtime()

        obj: ExternalIdp
        objs = runtime.external_idps
        for obj in objs:
            if obj.name == self.kwargs['pk']:
                break
        
        groups = obj.provider.get_groups()
        # users = obj.provider.get_users()

        # TODO: 
        # 1. move to background
        # 2. do the real import
        return JsonResponse(data=groups, safe=False)
        
