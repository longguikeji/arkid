from django.db import models
from django.http import Http404
from django.http.response import JsonResponse
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_extensions.mixins import NestedViewSetMixin
from django.contrib.auth.models import User as DUser
from tenant.models import Tenant
from inventory.models import (
    User
)
from api.v1.serializers.user import (
    UserSerializer, UserListResponsesSerializer
)
from api.v1.serializers.app import AppBaseInfoSerializer
from common.paginator import DefaultListPaginator
from .base import BaseViewSet
from app.models import App
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.decorators import action


@extend_schema_view(
    list=extend_schema(
        responses=UserListResponsesSerializer
    )
)
@extend_schema(
    tags=['user'],
)
class UserViewSet(BaseViewSet):

    # permission_classes = [IsAuthenticated]
    # authentication_classes = [ExpiringTokenAuthentication]

    model = User

    permission_classes = []
    authentication_classes = []

    serializer_class = UserSerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        context = self.get_serializer_context()
        tenant = context['tenant']

        group = self.request.query_params.get('group', None)

        kwargs = {
            'tenants__in': [tenant],
        }

        if group is not None:
            kwargs['groups__uuid__in'] = group.split(',')

        qs = User.objects.filter(**kwargs).order_by('id')
        return qs

    def get_object(self):
        context = self.get_serializer_context()
        tenant = context['tenant']

        kwargs = {
            'tenants__in': [tenant],
            'uuid': self.kwargs['pk'],
        }

        return User.valid_objects.filter(**kwargs).first()


@extend_schema(
    tags=['user-app']
)
class UserAppViewSet(BaseViewSet):

    # permission_classes = [IsAuthenticated]
    # authentication_classes = [ExpiringTokenAuthentication]

    model = App

    permission_classes = []
    authentication_classes = []

    serializer_class = AppBaseInfoSerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        context = self.get_serializer_context()
        tenant = context['tenant']
        user = context['user']
        all_apps = App.active_objects.filter(
            tenant=tenant,
        )
        if tenant.has_admin_perm(user) or user.is_superuser:
            objs = all_apps
        else:
            all_apps_perms = [app.access_perm_code for app in all_apps]
            perms = set([perm.codename for perm in user.user_permissions.filter(
                codename__in=all_apps_perms
            )])
            groups = user.groups.all()
            g: Group
            for g in groups:
                perms = perms | set([perm.codename for perm in g.owned_perms(all_apps_perms)])
            objs = [app for app in all_apps if app.access_perm_code in perms]
        return objs
