from inventory.models import (
    Group
)
from api.v1.serializers.group import (
    GroupSerializer, 
    GroupListResponseSerializer,
    GroupCreateRequestSerializer, 
    GroupCreateResponseSerializer
)
from common.paginator import DefaultListPaginator
from .base import BaseViewSet
from drf_spectacular.utils import extend_schema,extend_schema_view, OpenApiParameter
from drf_spectacular.openapi import OpenApiTypes

@extend_schema_view(
    list=extend_schema(
        responses=GroupSerializer,
        parameters=[
            OpenApiParameter("parent", OpenApiTypes.UUID, OpenApiParameter.QUERY, description='group.uuid'),
        ]
    ),
    create=extend_schema(
        request=GroupCreateRequestSerializer,
        responses=GroupSerializer,
    ),
    retrieve=extend_schema(
        responses=GroupSerializer,
    ),
    update=extend_schema(
        request=GroupSerializer,
        responses=GroupSerializer,
    ),
)
@extend_schema(
    tags = ['group']
)
class GroupViewSet(BaseViewSet):

    # permission_classes = [IsAuthenticated]
    # authentication_classes = [ExpiringTokenAuthentication]

    model = Group

    permission_classes = []
    authentication_classes = []

    serializer_class = GroupSerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        context = self.get_serializer_context()
        tenant = context['tenant']

        parent = self.request.query_params.get('parent', None)

        kwargs = {
            'tenant': tenant,
        }

        if parent is None:
            kwargs['parent'] = None
        else:
            kwargs['parent__uuid'] = parent

        qs = Group.valid_objects.filter(**kwargs).order_by('id')
        return qs
    
    def get_object(self):
        context = self.get_serializer_context()
        tenant = context['tenant']

        kwargs = {
            'tenant': tenant,
            'uuid': self.kwargs['pk'],
        }

        obj = Group.valid_objects.filter(**kwargs).first()
        return obj