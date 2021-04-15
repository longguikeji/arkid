from django.db import models
from django.http import Http404
from django.http.response import JsonResponse
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_extensions.mixins import NestedViewSetMixin
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from django.contrib.auth.models import User as DUser
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from tenant.models import Tenant
from inventory.models import User
from inventory.resouces import UserResource
from api.v1.serializers.user import (
    UserSerializer,
    UserListResponsesSerializer,
    TokenSerializer,
    TokenRequestSerializer,
    UserImportSerializer,
)
from api.v1.serializers.app import AppBaseInfoSerializer
from common.paginator import DefaultListPaginator
from .base import BaseViewSet
from app.models import App
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.decorators import action
from tablib import Dataset
from collections import defaultdict


@extend_schema_view(list=extend_schema(responses=UserListResponsesSerializer))
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
        request=UserImportSerializer,
        # responses=ExternalIdpReorderSerializer,
    )
    @action(detail=False, methods=['post'])
    def user_import(self, request, *args, **kwargs):
        context = self.get_serializer_context()
        tenant = context['tenant']
        support_content_types = [
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-excel',
        ]
        upload = request.data.get("file", None)  # 设置默认值None
        if not upload:
            return Response({'error': '1', 'message': 'No file find in form dada'})
        if upload.content_type not in support_content_types:
            return Response({'error': '1', 'message': 'ContentType Not Support!'})
        user_resource = UserResource()
        dataset = Dataset()
        imported_data = dataset.load(upload.read())
        result = user_resource.import_data(
            dataset, dry_run=True, tenant_id=tenant.id
        )  # Test the data import
        if not result.has_errors() and not result.has_validation_errors():
            user_resource.import_data(dataset, dry_run=False)
            return Response({'error': '0', 'message': result.totals})
        else:
            base_errors = result.base_errors
            if base_errors:
                base_errors = [err.error for err in base_errors]
            row_errors = result.row_errors()
            row_errors_dict = defaultdict(list)
            if row_errors:
                for lineno, err_list in row_errors:
                    for err in err_list:
                        row_errors_dict[lineno].append(str(err.error))

            invalid_rows = result.invalid_rows
            if invalid_rows:
                invalid_rows = [err.error for err in base_errors]

            return Response(
                {
                    'error': '1',
                    'message': {
                        'base_errors': base_errors,
                        'row_errors': row_errors_dict,
                        'invalid_rows': invalid_rows,
                    },
                }
            )


@extend_schema(tags=['user-app'])
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
            perms = set(
                [
                    perm.codename
                    for perm in user.user_permissions.filter(
                        codename__in=all_apps_perms
                    )
                ]
            )
            groups = user.groups.all()
            g: Group
            for g in groups:
                perms = perms | set(
                    [perm.codename for perm in g.owned_perms(all_apps_perms)]
                )
            objs = [app for app in all_apps if app.access_perm_code in perms]
        return objs


@extend_schema(tags=['user'])
class TokenView(generics.CreateAPIView):
    permission_classes = []
    authentication_classes = []

    serializer_class = TokenRequestSerializer

    @extend_schema(responses=TokenSerializer)
    def post(self, request):
        key = request.data.get('token', '')
        expiring_token = ExpiringTokenAuthentication()
        is_valid = True
        try:
            expiring_token.authenticate_credentials(key)
        except Exception as e:
            is_valid = False
        return Response(is_valid)
