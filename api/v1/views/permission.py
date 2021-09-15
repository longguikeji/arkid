from django.http import Http404
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api.v1.serializers.permission import (
    PermissionSerializer, PermissionCreateSerializer, PermissionGroupListSerializer,
    PermissionGroupCreateSerializer, UserPermissionListSerializer,
)
from tenant.models import (
    Tenant,
)
from common.paginator import DefaultListPaginator
from openapi.utils import extend_schema
from drf_spectacular.utils import OpenApiParameter
from .base import BaseTenantViewSet
from inventory.models import Permission, PermissionGroup, User
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


@extend_schema(
    roles=['tenant admin', 'global admin'],
    tags=['permission'],
    parameters=[
        OpenApiParameter(
            name='name',
            type={'type': 'string'},
            location=OpenApiParameter.QUERY,
            required=False,
        )
    ]
)
class UserPermissionView(generics.RetrieveAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = UserPermissionListSerializer

    def get(self, request, tenant_uuid, user_uuid):
        name = self.request.query_params.get('name', '')
        user = User.active_objects.filter(uuid=user_uuid).first()
        items = []
        # 当前用户拥有的权限
        user_permissions = user.user_permissions.filter(is_del=False, tenant__uuid=tenant_uuid).all()
        for user_permission in user_permissions:
            items.append({
                'uuid': user_permission.uuid_hex,
                'name': user_permission.name,
                'is_system': user_permission.is_system_permission,
                'source': '用户权限'
            })
        # 当前用户拥有的权限组
        user_permissions_groups = user.user_permissions_group.filter(is_del=False, tenant__uuid=tenant_uuid).all()
        for user_permissions_group in user_permissions_groups:
            items.append({
                'uuid': user_permissions_group.uuid_hex,
                'name': user_permissions_group.name,
                'is_system': user_permissions_group.is_system_group,
                'source': '用户权限组'
            })
        # 当前用户所属分组拥有的权限
        groups = user.groups.all()
        for group in groups:
            for permission in group.permissions.filter(is_del=False, tenant__uuid=tenant_uuid).all():
                items.append({
                    'uuid': permission.uuid_hex,
                    'name': permission.name,
                    'is_system': permission.is_system_permission,
                    'source': '用户组权限'
                })
        # 当前用户所属分组用户的组权限
        groups = user.groups.all()
        for group in groups:
            for permissions_group in group.permissions_groups.filter(is_del=False, tenant__uuid=tenant_uuid).all():
                items.append({
                    'uuid': permissions_group.uuid_hex,
                    'name': permissions_group.name,
                    'is_system': permissions_group.is_system_group,
                    'source': '用户组权限组'
                })
        if name:
            temp_list = []
            for item in items:
                search_name = item.get('name')
                if name in search_name:
                    temp_list.append(item)
            items = temp_list
        serializer = self.get_serializer(
            {'items': items}
        )
        return Response(serializer.data)

