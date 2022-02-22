from django.http import Http404
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api.v1.serializers.permission import (
    PermissionSerializer, PermissionCreateSerializer, PermissionGroupListSerializer,
    PermissionGroupCreateSerializer, UserPermissionListSerializer, UserPermissionCreateSerializer,
    UserPermissionDeleteSerializer, GroupPermissionListSerializer, GroupPermissionCreateSerializer,
    GroupPermissionDeleteSerializer, AppPermissionSerializer,
)
from tenant.models import (
    Tenant,
)
from common.paginator import DefaultListPaginator
from openapi.utils import extend_schema
from drf_spectacular.utils import OpenApiParameter
from drf_spectacular.openapi import OpenApiTypes
from .base import BaseTenantViewSet
from inventory.models import Permission, PermissionGroup, User, Group
from rest_framework import viewsets
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication

from django.db.models import Q


@extend_schema(
    roles=['tenantadmin', 'globaladmin'],
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

        group_uuid = self.request.query_params.get('group', None)
        if not group_uuid:
            # ids = []
            # objs = Permission.valid_objects.filter(
            #     tenant=tenant,
            # ).order_by('id')
            # for obj in objs:
            #     if obj.app is None:
            #         ids.append(obj.id)
            #     elif obj.app.is_del is False:
            #         ids.append(obj.id)
            # 系统权限
            # objs = Permission.valid_objects.filter(
            #     id__in=ids,
            # ).order_by('id')
            objs = Permission.valid_objects.filter(
                Q(tenant=tenant)|Q(is_system_permission=True)
            ).order_by('-id')
            return objs

        kwargs = {
            'uuid': group_uuid,
        }

        group = PermissionGroup.valid_objects.filter(
            Q(tenant=tenant)|Q(is_system_group=True)
        ).filter(**kwargs).first()
        return group.permissions.all()

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
    roles=['tenantadmin', 'globaladmin'],
    tags=['permission']
)
class PermissionCreateView(generics.CreateAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = PermissionCreateSerializer

    def create(self, request, *args, **kwargs):
        context = self.get_serializer_context()
        return super(PermissionCreateView, self).create(request, *args, **kwargs)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['tenant'] = Tenant.objects.filter(uuid=self.kwargs['tenant_uuid']).first()
        return context


@extend_schema(
    roles=['tenantadmin', 'globaladmin'],
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
    roles=['tenantadmin', 'globaladmin'],
    tags=['permission'],
    parameters=[
        OpenApiParameter(
            "parent",
            OpenApiTypes.UUID,
            OpenApiParameter.QUERY,
            description='permission_group.uuid',
            required=False,
        ),
    ],
)
class PermissionGroupView(generics.ListAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = PermissionGroupListSerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        parent = self.request.query_params.get('parent', None)
        tenant_uuid = self.kwargs['tenant_uuid']

        kwargs = {
            
        }

        if parent is None:
            kwargs['parent'] = None
        else:
            kwargs['parent__uuid'] = parent

        permission_groups = PermissionGroup.valid_objects.filter(Q(tenant__uuid=tenant_uuid)|Q(is_system_group=True)).filter(**kwargs).order_by('-id')
        return permission_groups


@extend_schema(
    roles=['tenantadmin', 'globaladmin'],
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
    roles=['tenantadmin', 'globaladmin'],
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
    roles=['tenantadmin', 'globaladmin'],
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
        name = request.query_params.get('name', '')
        user = User.active_objects.filter(uuid=user_uuid).first()
        items = []
        # 当前用户拥有的权限
        user_permissions = user.user_permissions.filter(is_del=False, tenant__uuid=tenant_uuid).all()
        for user_permission in user_permissions:
            items.append({
                'uuid': user_permission.uuid_hex,
                'name': user_permission.name,
                'is_system': user_permission.is_system_permission,
                'app_name': user_permission.app_name,
                'source': '用户权限',
            })
        # 当前用户拥有的权限组
        user_permissions_groups = user.user_permissions_group.filter(is_del=False, tenant__uuid=tenant_uuid).all()
        for user_permissions_group in user_permissions_groups:
            items.append({
                'uuid': user_permissions_group.uuid_hex,
                'name': user_permissions_group.name,
                'is_system': user_permissions_group.is_system_group,
                'app_name': '',
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
                    'app_name': '',
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
                    'app_name': '',
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


@extend_schema(
    roles=['tenantadmin', 'globaladmin'],
    tags=['permission']
)
class UserPermissionCreateView(generics.CreateAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = UserPermissionCreateSerializer

    def create(self, request, *args, **kwargs):
        context = self.get_serializer_context()
        tenant = context['tenant']
        user = request.user
        check_result = user.check_permission(tenant)
        if not check_result is None:
            return check_result
        return super(UserPermissionCreateView, self).create(request, *args, **kwargs)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = User.objects.filter(uuid=self.kwargs['user_uuid']).first()
        context['tenant'] = Tenant.objects.filter(uuid=self.kwargs['tenant_uuid']).first()
        return context


@extend_schema(
    roles=['tenantadmin', 'globaladmin'],
    tags=['permission'],
    parameters=[
        OpenApiParameter(
            name='uuid',
            type={'type': 'string'},
            location=OpenApiParameter.QUERY,
            required=True,
        ),
        OpenApiParameter(
            name='source',
            type={'type': 'string'},
            location=OpenApiParameter.QUERY,
            required=True,
        ),
    ]
)
class UserPermissionDeleteView(generics.RetrieveAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = UserPermissionDeleteSerializer

    def get(self, request, tenant_uuid, user_uuid):
        uuid = request.query_params.get('uuid', '')
        source = request.query_params.get('source', '')
        user = User.objects.filter(uuid=user_uuid).first()
        serializer = self.get_serializer(
            {'is_delete': True}
        )
        if uuid and source:
            if source == '用户权限':
                permission = Permission.valid_objects.filter(uuid=uuid).first()
                if permission:
                    user.user_permissions.remove(permission)
                else:
                    serializer = self.get_serializer(
                        {'is_delete': False}
                    )
            elif source == '用户权限组':
                permission_group = PermissionGroup.valid_objects.filter(uuid=uuid).first()
                if permission_group:
                    user.user_permissions_group.remove(permission_group)
                else:
                    serializer = self.get_serializer(
                        {'is_delete': False}
                    )
            else:
                serializer = self.get_serializer(
                    {'is_delete': False}
                )
        else:
            serializer = self.get_serializer(
                {'is_delete': False}
            )
        return Response(serializer.data)


# group
@extend_schema(
    roles=['tenantadmin', 'globaladmin'],
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
class GroupPermissionView(generics.RetrieveAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = GroupPermissionListSerializer

    def get(self, request, tenant_uuid, group_uuid):
        name = request.query_params.get('name', '')
        group = Group.active_objects.filter(uuid=group_uuid).first()
        items = []
        # 当前分组拥有的权限
        permissions = group.permissions.filter(is_del=False, tenant__uuid=tenant_uuid).all()
        for permission in permissions:
            items.append({
                'uuid': permission.uuid_hex,
                'name': permission.name,
                'is_system': permission.is_system_permission,
                'app_name': permission.app_name,
                'source': '分组权限',
            })
        # 当前分组拥有的权限组
        permissions_groups = group.permissions_groups.filter(is_del=False, tenant__uuid=tenant_uuid).all()
        for permissions_group in permissions_groups:
            items.append({
                'uuid': permissions_group.uuid_hex,
                'name': permissions_group.name,
                'is_system': permissions_group.is_system_group,
                'app_name': '',
                'source': '分组权限组'
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


@extend_schema(
    roles=['tenantadmin', 'globaladmin'],
    tags=['permission']
)
class GroupPermissionCreateView(generics.CreateAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = GroupPermissionCreateSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['group'] = Group.objects.filter(uuid=self.kwargs['group_uuid']).first()
        return context


@extend_schema(
    roles=['tenantadmin', 'globaladmin'],
    tags=['permission'],
    parameters=[
        OpenApiParameter(
            name='uuid',
            type={'type': 'string'},
            location=OpenApiParameter.QUERY,
            required=True,
        ),
        OpenApiParameter(
            name='source',
            type={'type': 'string'},
            location=OpenApiParameter.QUERY,
            required=True,
        ),
    ]
)
class GroupPermissionDeleteView(generics.RetrieveAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = GroupPermissionDeleteSerializer

    def get(self, request, tenant_uuid, group_uuid):
        uuid = request.query_params.get('uuid', '')
        source = request.query_params.get('source', '')
        group = Group.objects.filter(uuid=group_uuid).first()
        serializer = self.get_serializer(
            {'is_delete': True}
        )
        if uuid and source:
            if source == '分组权限':
                permission = Permission.valid_objects.filter(uuid=uuid).first()
                if permission and permission.is_system_permission is False:
                    group.permissions.remove(permission)
                else:
                    serializer = self.get_serializer(
                        {'is_delete': False}
                    )
            elif source == '分组权限组':
                permission_group = PermissionGroup.valid_objects.filter(uuid=uuid).first()
                if permission_group and permission_group.is_system_group is False:
                    group.permissions_groups.remove(permission_group)
                else:
                    serializer = self.get_serializer(
                        {'is_delete': False}
                    )
            else:
                serializer = self.get_serializer(
                    {'is_delete': False}
                )
        else:
            serializer = self.get_serializer(
                {'is_delete': False}
            )
        return Response(serializer.data)


# app
@extend_schema(
    roles=['tenantadmin', 'globaladmin'],
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
class AppPermissionView(generics.ListAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = AppPermissionSerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        tenant_uuid = self.kwargs['tenant_uuid']
        app_uuid = self.kwargs['app_uuid']
        kwargs = {
            'tenant__uuid': tenant_uuid,
            'app__uuid': app_uuid,
        }
        name = self.request.query_params.get('name', '')
        if name:
            kwargs['name__icontains'] = name
        objs = Permission.valid_objects.filter(
            **kwargs
        ).order_by('id')
        return objs