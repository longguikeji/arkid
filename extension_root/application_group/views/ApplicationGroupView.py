from django.http import response
from common.paginator import DefaultListPaginator
from api.v1.views.base import BaseViewSet
from drf_spectacular.utils import extend_schema_view
from extension_root.application_group.serializers.ApplicationGroupListSerializer import ApplicationGroupListSerializer
from inventory.models import User
from openapi.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from ..models import ApplicationGroup
from ..serializers import BaseApplicationGroupSerializer,ApplicationGroupCreateSerializer,ApplicationGroupListSerializer
from app.models import App
from django.http.response import JsonResponse


@extend_schema_view(
    list=extend_schema(
        responses=ApplicationGroupListSerializer,
        roles=['tenant admin', 'global admin', 'general user'],
    ),
    retrieve=extend_schema(
        responses=ApplicationGroupCreateSerializer,
        roles=['tenant admin', 'global admin'],
    ),
    create=extend_schema(
        request=ApplicationGroupCreateSerializer,
        responses=ApplicationGroupCreateSerializer,
        roles=['tenant admin', 'global admin']
    ),
    update=extend_schema(
        request=ApplicationGroupCreateSerializer,
        responses=ApplicationGroupCreateSerializer,
        roles=['tenant admin', 'global admin']
    ),
    destroy=extend_schema(roles=['tenant admin', 'global admin']),
    partial_update=extend_schema(roles=['tenant admin', 'global admin']),
)
class ApplicationGroupViewSet(BaseViewSet):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = BaseApplicationGroupSerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        context = self.get_serializer_context()
        tenant = context['tenant']
        qs = ApplicationGroup.active_objects.filter(
            tenant=tenant).distinct().order_by('-id').all()
        return qs

    def get_object(self):
        uuid = self.kwargs['pk']
        context = self.get_serializer_context()
        tenant = context['tenant']

        return (
            ApplicationGroup.active_objects.filter(
                tenant=tenant,
                uuid=uuid,
            )
            .order_by('id')
            .first()
        )
    
    def update(self, request, *args, **kwargs):
        print(1111, request.data)
        serializer = ApplicationGroupCreateSerializer(
            context = self.get_serializer_context(),
            data=request.data,
            instance=self.get_object()
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return JsonResponse(
            data={
                "status": 200,
                "data": serializer.data
            }
        )

    
    def create(self, request, *args, **kwargs):
        serializer = ApplicationGroupCreateSerializer(
            context = self.get_serializer_context(),
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return JsonResponse(
            data={
                "status": 200,
                "data": serializer.data
            }
        )
        
    def delete(self,request, *args, **kwargs):
        self.get_object().delete()
        return JsonResponse(
            data={
                "status": 200,
            }
        )
