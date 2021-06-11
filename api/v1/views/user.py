import json
import datetime
from django.db import models
from django.http import Http404
from django.http.response import JsonResponse
from django.utils.translation import gettext_lazy as _
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
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
    UserInfoSerializer,
    UserBindInfoSerializer,
    PasswordSerializer,
    PasswordRequestSerializer,
    LogoutSerializer,
    UserManageTenantsSerializer,
)
from api.v1.serializers.app import AppBaseInfoSerializer
from common.paginator import DefaultListPaginator
from .base import BaseViewSet
from app.models import App
from openapi.utils import extend_schema
from drf_spectacular.utils import extend_schema_view
from rest_framework.decorators import action
from tablib import Dataset
from collections import defaultdict
from common.code import Code
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from drf_spectacular.openapi import OpenApiTypes


@extend_schema_view(
    list=extend_schema(roles=['tenant admin', 'global admin'], responses=UserListResponsesSerializer),
    retrieve=extend_schema(roles=['tenant admin', 'global admin']),
    create=extend_schema(roles=['tenant admin', 'global admin']),
    update=extend_schema(roles=['tenant admin', 'global admin']),
    destroy=extend_schema(roles=['tenant admin', 'global admin']),
    partial_update=extend_schema(roles=['tenant admin', 'global admin']),
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
            'is_del': False,
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

    def destroy(self, request, *args, **kwargs):
        self.get_object().kill()
        return Response(
            {
                'error_code': 0,
                'error_msg': '删除成功',
            }
        )

    def create(self, request, *args, **kwargs):
        password = request.data.get('password')
        if not password:
            return JsonResponse(data={
                'error': Code.PASSWORD_NONE_ERROR.value,
                'message': _('password is empty'),
            })
        if self.check_password(password) is False:
            return JsonResponse(data={
                'error': Code.PASSWORD_STRENGTH_ERROR.value,
                'message': _('password strength not enough'),
            })
        return super(UserViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        password = request.data.get('password')
        if password and self.check_password(password) is False:
            return JsonResponse(data={
                'error': Code.PASSWORD_STRENGTH_ERROR.value,
                'message': _('password strength not enough'),
            })
        return super(UserViewSet, self).update(request, *args, **kwargs)

    def check_password(self, pwd):
        if pwd.isdigit() or len(pwd) < 8:
            return False
        return True

    @extend_schema(
        roles=['tenant admin', 'global admin'],
        request=UserImportSerializer,
        responses=UserImportSerializer,
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
            return Response(
                {
                    'error': Code.USER_IMPORT_ERROR.value,
                    'message': 'No file find in form dada',
                }
            )
        if upload.content_type not in support_content_types:
            return Response(
                {
                    'error': Code.USER_IMPORT_ERROR.value,
                    'message': 'ContentType Not Support!',
                }
            )
        user_resource = UserResource()
        dataset = Dataset()
        imported_data = dataset.load(upload.read())
        result = user_resource.import_data(
            dataset, dry_run=True, tenant_id=tenant.id
        )  # Test the data import
        if not result.has_errors() and not result.has_validation_errors():
            user_resource.import_data(dataset, dry_run=False, tenant_id=tenant.id)
            return Response(
                {'error': Code.OK.value, 'message': json.dumps(result.totals)}
            )
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
                    'error': Code.USER_IMPORT_ERROR.value,
                    'message': json.dumps(
                        {
                            'base_errors': base_errors,
                            'row_errors': row_errors_dict,
                            'invalid_rows': invalid_rows,
                        }
                    ),
                }
            )

    @extend_schema(
        roles=['tenant admin', 'global admin'],
        responses={(200, 'application/octet-stream'): OpenApiTypes.BINARY},
    )
    @action(detail=False, methods=['get'])
    def user_export(self, request, *args, **kwargs):
        context = self.get_serializer_context()
        tenant = context['tenant']
        kwargs = {
            'tenants__in': [tenant],
        }
        qs = User.objects.filter(**kwargs).order_by('id')
        data = UserResource().export(qs)
        export_data = data.xlsx
        content_type = 'application/octet-stream'
        response = HttpResponse(export_data, content_type=content_type)
        date_str = datetime.datetime.now().strftime('%Y-%m-%d')
        filename = '%s-%s.%s' % ('User', date_str, 'xlsx')
        response['Content-Disposition'] = 'attachment; filename="%s"' % (filename)
        return response


@extend_schema_view(
    list=extend_schema(roles=['general user', 'tenant admin', 'global admin']),
    create=extend_schema(roles=['general user', 'tenant admin', 'global admin']),
    retrieve=extend_schema(roles=['general user', 'tenant admin', 'global admin']),
    destroy=extend_schema(roles=['general user', 'tenant admin', 'global admin']),
    update=extend_schema(roles=['general user', 'tenant admin', 'global admin']),
    partial_update=extend_schema(roles=['general user', 'tenant admin', 'global admin']),
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
class UserTokenView(generics.CreateAPIView):
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


@extend_schema(tags=['user'])
class UpdatePasswordView(generics.CreateAPIView):
    permission_classes = []
    authentication_classes = []

    serializer_class = PasswordRequestSerializer

    @extend_schema(
        roles=['tenant admin', 'global admin', 'general user'],
        responses=PasswordSerializer
    )
    def post(self, request):
        uuid = request.data.get('uuid', '')
        password = request.data.get('password', '')
        old_password = request.data.get('old_password', '')
        user = User.objects.filter(uuid=uuid).first()
        is_succeed = True
        if not user:
            return JsonResponse(data={
                'error': Code.USER_EXISTS_ERROR.value,
                'message': _('user does not exist'),
            })
        if password and self.check_password(password) is False:
            return JsonResponse(data={
                'error': Code.PASSWORD_STRENGTH_ERROR.value,
                'message': _('password strength not enough'),
            })
        if password and user.check_password(old_password) is False:
            return JsonResponse(data={
                'error': Code.OLD_PASSWORD_ERROR.value,
                'message': _('old password error'),
            })
        try:
            user.set_password(password)
            user.save()
        except Exception as e:
            is_succeed = False
        return Response(is_succeed)

    def check_password(self, pwd):
        if pwd.isdigit() or len(pwd) < 8:
            return False
        return True


@extend_schema(roles=['general user', 'tenant admin', 'global admin'], tags=['user'])
class UserInfoView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]
    serializer_class = UserInfoSerializer

    @extend_schema(responses=UserInfoSerializer)
    def get_object(self):
        return self.request.user


@extend_schema(tags=['user'])
class UserBindInfoView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    authentication_classes = [ExpiringTokenAuthentication]
    serializer_class = UserBindInfoSerializer

    @extend_schema(roles=['general user', 'tenant admin', 'global admin'], responses=UserBindInfoSerializer)
    def get(self, request):
        from extension_root.feishu.models import FeishuUser
        from extension_root.gitee.models import GiteeUser
        from extension_root.github.models import GithubUser
        from extension_root.arkid.models import ArkIDUser
        from extension_root.miniprogram.models import MiniProgramUser
        user = request.user
        feishuusers = FeishuUser.valid_objects.filter(user=request.user)
        giteeusers = GiteeUser.valid_objects.filter(user=request.user)
        githubusers = GithubUser.valid_objects.filter(user=request.user)
        arkidusers = ArkIDUser.valid_objects.filter(user=request.user)
        miniprogramusers = MiniProgramUser.valid_objects.filter(user=request.user)
        result = []
        for item in feishuusers:
            result.append({
                'name': '飞书',
                'tenant': item.tenant.uuid,
                'unbind': '/api/v1/tenant/{}/feishu/unbind'.format(item.tenant.uuid),
            })
        for item in giteeusers:
            result.append({
                'name': 'gitee',
                'tenant': item.tenant.uuid,
                'unbind': '/api/v1/tenant/{}/gitee/unbind'.format(item.tenant.uuid),
            })
        for item in githubusers:
            result.append({
                'name': 'github',
                'tenant': item.tenant.uuid,
                'unbind': '/api/v1/tenant/{}/github/unbind'.format(item.tenant.uuid),
            })
        for item in arkidusers:
            result.append({
                'name': 'arkid',
                'tenant': item.tenant.uuid,
                'unbind': '/api/v1/tenant/{}/arkid/unbind'.format(item.tenant.uuid),
            })
        for item in miniprogramusers:
            result.append({
                'name': '微信小程序',
                'tenant': item.tenant.uuid,
                'unbind': '/api/v1/tenant/{}/miniprogram/unbind'.format(item.tenant.uuid),
            })
        return JsonResponse({'data': result}, safe=False)


@extend_schema(tags=['user'])
class UserLogoutView(generics.RetrieveAPIView):

    @extend_schema(responses=LogoutSerializer)
    def get(self, request):
        user = request.user
        is_succeed = False
        if user and user.username:
            from rest_framework.authtoken.models import Token
            Token.objects.filter(
                user=user
            ).delete()
            is_succeed = True
        return Response({
            "is_succeed": is_succeed
        })


@extend_schema(tags=['user'])
class UserManageTenantsView(generics.RetrieveAPIView):

    @extend_schema(roles=['general user', 'tenant admin', 'global admin'], responses=UserManageTenantsSerializer)
    def get(self, request):
        user = request.user
        if user and user.username:
            return Response({
                "manage_tenants": user.manage_tenants(),
                "is_global_admin": user.is_superuser,
            })
