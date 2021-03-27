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
    UserSerializer
)
from common.paginator import DefaultListPaginator
from .base import BaseViewSet
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action

@extend_schema(
    tags = ['user']
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
    tags = ['user-app']
)
class UserAppViewSet(BaseViewSet):

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

        kwargs = {
            'tenants__in': [tenant],
        }

        objs = User.objects.filter(**kwargs).order_by('id')
        return objs