from common.paginator import DefaultListPaginator
from api.v1.views.base import BaseViewSet
from drf_spectacular.utils import extend_schema_view
from openapi.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from ..models import ApplicationMultipleIp
from ..serializers import BaseApplicationMultipleIpSerializer
from app.models import App
from django.http.response import JsonResponse


@extend_schema_view(
    destroy=extend_schema(roles=['tenant admin', 'global admin']),
    partial_update=extend_schema(roles=['tenant admin', 'global admin']),
)
@extend_schema(
    tags=['app'],
)
class ApplicationMultipleIpViewSet(BaseViewSet):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = BaseApplicationMultipleIpSerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        context = self.get_serializer_context()
        tenant = context['tenant']
        qs = ApplicationMultipleIp.active_objects.filter(
            app__tenant=tenant).order_by('id')
        return qs

    def get_object(self):
        uuid = self.kwargs['pk']
        context = self.get_serializer_context()
        tenant = context['tenant']

        return (
            ApplicationMultipleIp.active_objects.filter(
                app__tenant=tenant,
                uuid=uuid,
            )
            .order_by('id')
            .first()
        )
