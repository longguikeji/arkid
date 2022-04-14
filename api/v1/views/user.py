import json
import io
import datetime
import collections
from django.db import models
from django.http import Http404
from django.http.response import JsonResponse
from django.utils.translation import gettext_lazy as _
from common.excel_utils import export_excel, import_excel
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import ListModelMixin
from rest_framework_extensions.mixins import NestedViewSetMixin
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from django.contrib.auth.models import User as DUser
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from tenant.models import Tenant
from config.models import PasswordComplexity
from inventory.models import (
    User, Group, Invitation,
    UserAppData, UserTenantPermissionAndPermissionGroup,
)
from inventory.resouces import UserResource
from runtime import get_app_runtime
from external_idp.models import ExternalIdp
from extension.utils import find_available_extensions

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
    ResetPasswordRequestSerializer,
    MobileResetPasswordRequestSerializer,
    EmailResetPasswordRequestSerializer,
    UserLogoffSerializer,
    UserTokenExpireSerializer,
    UserAppDataSerializer,
    UserListSerializer,
    UserFreezeSerializer
)
from api.v1.serializers.app import AppBaseInfoSerializer
from api.v1.serializers.sms import ResetPWDSMSClaimSerializer
from api.v1.serializers.email import ResetPWDEmailClaimSerializer
from common.paginator import DefaultListPaginator
from .base import BaseViewSet
from app.models import App
from openapi.utils import extend_schema
from drf_spectacular.utils import extend_schema_view, OpenApiParameter
from rest_framework.decorators import action
from tablib import Dataset
from collections import defaultdict
from common.code import Code
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from drf_spectacular.openapi import OpenApiTypes
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from common.utils import check_password_complexity
from runtime import get_app_runtime
from perm.custom_access import ApiAccessPermission
import re
from webhook.manager import WebhookManager
from django.db import transaction


@extend_schema_view(
    list=extend_schema(
        roles=['tenantadmin', 'globaladmin', 'usermanage.userlist'],
        responses=UserListResponsesSerializer,
        parameters=[
            OpenApiParameter(
                name='name',
                type={'type': 'string'},
                location=OpenApiParameter.QUERY,
                required=False,
            ),
            OpenApiParameter(
                name='username',
                type={'type': 'string'},
                location=OpenApiParameter.QUERY,
                required=False,
            ),
            OpenApiParameter(
                name='mobile',
                type={'type': 'string'},
                location=OpenApiParameter.QUERY,
                required=False,
            ),
            OpenApiParameter(
                name='email',
                type={'type': 'string'},
                location=OpenApiParameter.QUERY,
                required=False,
            ),
            OpenApiParameter(
                name='country',
                type={'type': 'string'},
                location=OpenApiParameter.QUERY,
                required=False,
            ),
            OpenApiParameter(
                name='city',
                type={'type': 'string'},
                location=OpenApiParameter.QUERY,
                required=False,
            ),
            OpenApiParameter(
                name='job_title',
                type={'type': 'string'},
                location=OpenApiParameter.QUERY,
                required=False,
            ),
            OpenApiParameter(
                name='tenant_uuid',
                type={'type': 'string'},
                location=OpenApiParameter.QUERY,
                required=False,
            ),
        ], summary='用户列表'
    ),
    retrieve=extend_schema(roles=['tenantadmin', 'globaladmin', 'usermanage.userlist'], summary='读取用户'),
    create=extend_schema(roles=['tenantadmin', 'globaladmin', 'usermanage.userlist'], summary='创建用户'),
    update=extend_schema(roles=['tenantadmin', 'globaladmin', 'usermanage.userlist'], summary='更新用户'),
    destroy=extend_schema(roles=['tenantadmin', 'globaladmin', 'usermanage.userlist'], summary='删除用户'),
    partial_update=extend_schema(roles=['tenantadmin', 'globaladmin', 'usermanage.userlist'], summary='批量更新用户'),
)
@extend_schema(
    tags=['user'],
)
class UserViewSet(BaseViewSet):

    permission_classes = [IsAuthenticated, ApiAccessPermission]
    authentication_classes = [ExpiringTokenAuthentication]

    model = User

    serializer_class = UserSerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        user = self.request.user
        context = self.get_serializer_context()
        tenant = context['tenant']

        group = self.request.query_params.get('group', None)
        name = self.request.query_params.get('name', None)
        username = self.request.query_params.get('username', None)
        mobile = self.request.query_params.get('mobile', None)
        email = self.request.query_params.get('email', None)
        country = self.request.query_params.get('country', None)
        city = self.request.query_params.get('city', None)
        job_title = self.request.query_params.get('job_title', None)
        tenant_uuid = self.request.query_params.get('tenant_uuid', None)
        group1 = group
        kwargs = {
            'is_del': False,
        }
        if tenant_uuid:
            tenant = Tenant.valid_objects.filter(uuid=tenant_uuid).first()

        kwargs['tenants__in'] = [tenant]

        if group is not None:
            kwargs['groups__uuid__in'] = group.split(',')
        if name is not None:
            kwargs['nickname'] = name
        if username is not None:
            kwargs['username'] = username
        if mobile is not None:
            kwargs['mobile'] = mobile
        if email is not None:
            kwargs['email'] = email
        if country is not None:
            kwargs['country'] = country
        if city is not None:
            kwargs['city'] = city
        if job_title is not None:
            kwargs['job_title'] = job_title

        qs = User.objects.filter(**kwargs)
        if user.is_superuser is False and tenant.has_admin_perm(user) is False:
            userpermissions = UserTenantPermissionAndPermissionGroup.valid_objects.filter(
                tenant=tenant,
                user=user,
                permission__group_info__isnull=False,
            )
            group_ids = []
            for userpermission in userpermissions:
                group_info = userpermission.permission.group_info
                group_ids.append(group_info.id)
            if len(group_ids) == 0:
                group_ids.append(0)
            qs = qs.filter(groups__id__in=group_ids)
            if qs.count() == 0:
                qs = User.objects.filter(id=user.id)
        return qs.order_by('id')

    def get_object(self):
        context = self.get_serializer_context()
        tenant = context['tenant']

        kwargs = {
            'tenants__in': [tenant],
            'uuid': self.kwargs['pk'],
        }

        return User.valid_objects.filter(**kwargs).first()

    @transaction.atomic()
    def destroy(self, request, *args, **kwargs):
        context = self.get_serializer_context()
        tenant = context['tenant']
        user = self.get_object()
        self.get_object().kill()
        # WebhookManager.user_deleted(tenant.uuid, user)
        transaction.on_commit(lambda: WebhookManager.user_deleted(tenant.uuid, user))
        return Response(
            {
                'error_code': 0,
                'error_msg': '删除成功',
            }
        )

    def create(self, request, *args, **kwargs):

        email = request.data.get('email')
        if email and not re.match(
            r'^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$',
            email,
        ):
            return JsonResponse(
                data={
                    'error': Code.EMAIL_FROMAT_ERROR.value,
                    'message': _('email format error'),
                }
            )
        mobile = request.data.get('mobile')
        if mobile and not re.match(r'(^(1)\d{10}$)', mobile):
            return JsonResponse(
                data={
                    'error': Code.MOBILE_FROMAT_ERROR.value,
                    'message': _('mobile format error'),
                }
            )
        return super(UserViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):

        email = request.data.get('email')
        if email and not re.match(
            r'^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$',
            email,
        ):
            return JsonResponse(
                data={
                    'error': Code.EMAIL_FROMAT_ERROR.value,
                    'message': _('email format error'),
                }
            )
        mobile = request.data.get('mobile')
        if mobile and not re.match(r'(^(1)\d{10}$)', mobile):
            return JsonResponse(
                data={
                    'error': Code.MOBILE_FROMAT_ERROR.value,
                    'message': _('mobile format error'),
                }
            )
        return super(UserViewSet, self).update(request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin', 'usermanage.userlist'],
        request=UserImportSerializer,
        responses=UserImportSerializer,
        summary='导入用户',
    )
    @action(detail=False, methods=['post'])
    def user_import(self, request, *args, **kwargs):
        # context = self.get_serializer_context()
        # tenant = context['tenant']

        # support_content_types = [
        #     'application/csv',
        #     'text/csv',
        # ]
        # upload = request.data.get("file", None)  # 设置默认值None
        # if not upload:
        #     return Response(
        #         {
        #             'error': Code.USER_IMPORT_ERROR.value,
        #             'message': 'No file find in form dada',
        #         }
        #     )
        # if upload.content_type not in support_content_types:
        #     return Response(
        #         {
        #             'error': Code.USER_IMPORT_ERROR.value,
        #             'message': 'ContentType Not Support!',
        #         }
        #     )
        # user_resource = UserResource()
        # dataset = Dataset()
        # imported_data = dataset.load(
        #     io.StringIO(upload.read().decode('utf-8')), format='csv'
        # )
        # result = user_resource.import_data(
        #     dataset, dry_run=True, tenant_id=tenant.id
        # )  # Test the data import
        # for item in dataset:
        #     email = str(item[2])
        #     mobile = str(item[3])
        #     if email and not re.match(
        #         r'^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$',
        #         email,
        #     ):
        #         return JsonResponse(
        #             data={
        #                 'error': Code.EMAIL_FROMAT_ERROR.value,
        #                 'message': _('email format error:{}'.format(email)),
        #             }
        #         )
        #     if mobile and not re.match(r'(^(1)\d{10}$)', mobile):
        #         return JsonResponse(
        #             data={
        #                 'error': Code.MOBILE_FROMAT_ERROR.value,
        #                 'message': _('mobile format error:{}'.format(mobile)),
        #             }
        #         )
        # if not result.has_errors() and not result.has_validation_errors():
        #     user_resource.import_data(dataset, dry_run=False, tenant_id=tenant.id)
        #     return Response(
        #         {'error': Code.OK.value, 'message': json.dumps(result.totals)}
        #     )
        # else:
        #     base_errors = result.base_errors
        #     if base_errors:
        #         base_errors = [err.error for err in base_errors]
        #     row_errors = result.row_errors()
        #     row_errors_dict = defaultdict(list)
        #     if row_errors:
        #         for lineno, err_list in row_errors:
        #             for err in err_list:
        #                 row_errors_dict[lineno].append(str(err.error))

        #     invalid_rows = result.invalid_rows
        #     if invalid_rows:
        #         invalid_rows = [err.error for err in base_errors]

        #     return Response(
        #         {
        #             'error': Code.USER_IMPORT_ERROR.value,
        #             'message': json.dumps(
        #                 {
        #                     'base_errors': base_errors,
        #                     'row_errors': row_errors_dict,
        #                     'invalid_rows': invalid_rows,
        #                 }
        #             ),
        #         }
        #     )
        context = self.get_serializer_context()
        tenant = context['tenant']
        support_content_types = [
            'application/vnd.ms-excel',
        ]
        # 文件读取
        upload = request.data.get("file", None)
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
        # 解析数据
        items = import_excel(request.FILES['file'])
        mobiles = []
        usernames = []
        for item in items:
            username = str(item['username']).strip()
            mobile = str(int(item['mobile']) if item['mobile'] else '').strip()
            if mobile and not re.match(r'(^(1)\d{10}$)', mobile):
                return JsonResponse(
                    data={
                        'error': Code.MOBILE_FROMAT_ERROR.value,
                        'message': _('mobile format error:{}'.format(mobile)),
                    }
                )
            mobiles.append(mobile)
            usernames.append(username)
        exists_username_user = User.valid_objects.filter(username__in=usernames).first()
        if exists_username_user:
            return JsonResponse(
                data={
                    'error': Code.USERNAME_EXISTS_ERROR.value,
                    'message': _('username already exists:{}'.format(exists_username_user.username)),
                }
            )
        exists_mobile_user = User.valid_objects.filter(mobile__in=mobiles).first()
        if exists_mobile_user:
            return JsonResponse(
                data={
                    'error': Code.MOBILE_EXISTS_ERROR.value,
                    'message': _('mobile already exists:{}'.format(exists_mobile_user.mobile)),
                }
            )
        for item in items:
            username = str(item['username']).strip()
            mobile = str(int(item['mobile']) if item['mobile'] else '').strip()
            username = str(item['username']).strip()
            email = str(item['email']).strip()
            first_name = str(item['first_name']).strip()
            last_name = str(item['last_name']).strip()
            nickname = str(item['nickname']).strip()
            country = str(item['country']).strip()
            city = str(item['city']).strip()
            job_title = str(item['job_title']).strip()
            # 新建用户
            create_user = User()
            create_user.username = username
            create_user.mobile = mobile
            create_user.email = email
            create_user.first_name = first_name
            create_user.last_name = last_name
            create_user.nickname = nickname
            create_user.country = country
            create_user.city = city
            create_user.job_title = job_title
            create_user.save()
            # 给用户关联租户
            create_user.tenants.add(tenant)
        return Response(
            {'error': Code.OK.value, 'message': 'import user succeed'}
        )


    @extend_schema(
        roles=['tenantadmin', 'globaladmin', 'usermanage.userlist'],
        responses={(200, 'application/octet-stream'): OpenApiTypes.BINARY},
        summary='导出用户',
    )
    @action(detail=False, methods=['get'])
    def user_export(self, request, *args, **kwargs):
        # context = self.get_serializer_context()
        # tenant = context['tenant']

        # kwargs = {
        #     'tenants__in': [tenant],
        # }
        # qs = User.active_objects.filter(**kwargs).order_by('id')
        # data = UserResource().export(qs)
        # export_data = data.csv
        # content_type = 'application/octet-stream'
        # response = HttpResponse(export_data, content_type=content_type)
        # date_str = datetime.datetime.now().strftime('%Y-%m-%d')
        # filename = '%s-%s.%s' % ('User', date_str, 'csv')
        # response['Content-Disposition'] = 'attachment; filename="%s"' % (filename)
        # return response
        context = self.get_serializer_context()
        users = self.get_queryset()
        records = []
        headers = [
            'username',
            'email',
            'mobile',
            'first_name',
            'last_name',
            'nickname',
            'country',
            'city',
            'job_title',
        ]
        for user in users:
            app = collections.OrderedDict()
            app['username'] = user.username
            app['email'] = user.email
            app['mobile'] = user.mobile
            app['first_name'] = user.first_name
            app['last_name'] = user.last_name
            app['nickname'] = user.nickname
            app['country'] = user.country
            app['city'] = user.city
            app['job_title'] = user.job_title
            records.append(app)
        name = 'user_{}'.format(datetime.datetime.now().strftime('%Y%m%d'))
        export_data = export_excel(headers, records, name)

        content_type = 'application/vnd.ms-excel'
        response = HttpResponse(export_data, content_type=content_type)
        response['Content-Disposition'] = 'attachment; filename="%s.xls"' % (
            name)
        return response


@extend_schema_view(
    list=extend_schema(roles=['tenantadmin', 'globaladmin', 'generaluser'], summary='租户app列表'),
    create=extend_schema(roles=['tenantadmin', 'globaladmin'], summary='租户app创建'),
    retrieve=extend_schema(roles=['tenantadmin', 'globaladmin'], summary='租户app详情'),
    destroy=extend_schema(roles=['tenantadmin', 'globaladmin'], summary='租户app删除'),
    update=extend_schema(roles=['tenantadmin', 'globaladmin'], summary='租户app修改'),
    partial_update=extend_schema(roles=['tenantadmin', 'globaladmin'], summary='租户app修改'),
)
@extend_schema(tags=['user-app'])
class UserAppViewSet(BaseViewSet):

    permission_classes = [IsAuthenticated, ApiAccessPermission]
    authentication_classes = [ExpiringTokenAuthentication]

    model = App

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
                    perm.permission.codename
                    for perm in UserTenantPermissionAndPermissionGroup.valid_objects.filter(
                        user=user,
                        permission__codename__in=all_apps_perms
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
        
        runtime = get_app_runtime()
        for provider_name in runtime.application_manage_providers:
            objs = runtime.application_manage_providers.get(provider_name)().get_queryset(objs=objs,view_instance=self)    
        
        return objs
    
    def list(self, request, *args, **kwargs):
        
        rs = super().list(request,*args,**kwargs)
        objs = self.get_queryset()
        runtime = get_app_runtime()
        for provider_name in runtime.application_manage_providers:
            rs = runtime.application_manage_providers.get(provider_name)().list_view(request=request,rs=rs,tenant=self.get_serializer_context()['tenant'],objs=objs,*args,**kwargs)
            
        return rs



@extend_schema(
    roles=['generaluser', 'tenantadmin', 'globaladmin'],
    tags=['user'],
    summary='获取用户token'
)
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


@extend_schema(roles=['generaluser', 'tenantadmin', 'globaladmin'], tags=['user'], summary='用户app数据')
class UserAppDataView(generics.RetrieveUpdateAPIView):

    permission_classes = [IsAuthenticated, ApiAccessPermission]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = UserAppDataSerializer

    def get_object(self):
        tenant_uuid = self.kwargs['tenant_uuid']
        tenant = Tenant.active_objects.get(uuid=tenant_uuid)
        user = self.request.user
        userappdata = UserAppData.active_objects.filter(user=user, tenant=tenant).first()
        if userappdata is None:
            userappdata = UserAppData()
            userappdata.user = user
            userappdata.tenant = tenant
            userappdata.data = []
            userappdata.save()
        return userappdata

    @extend_schema(
        roles=['tenantadmin', 'globaladmin', 'generaluser'],
        summary='用户app数据获取'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin', 'generaluser'],
        summary='用户app数据修改'
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin', 'generaluser'],
        summary='用户app数据修改'
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


@extend_schema(
    roles=['generaluser', 'tenantadmin', 'globaladmin'],
    tags=['user'],
    parameters=[
        OpenApiParameter(
            name='tenant',
            type={'type': 'string'},
            location=OpenApiParameter.QUERY,
            required=True,
        )
    ],
)
class UpdatePasswordView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, ApiAccessPermission]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = PasswordRequestSerializer

    @extend_schema(
        roles=['tenantadmin', 'globaladmin', 'generaluser'],
        responses=PasswordSerializer,
        summary='修改用户密码',
    )
    def post(self, request):
        tenant_uuid = self.request.query_params.get('tenant')
        if not tenant_uuid:
            tenant = None
        else:
            tenant = Tenant.valid_objects.filter(uuid=tenant_uuid).first()
        new_password = request.data.get('new_password', '')
        old_password = request.data.get('old_password', '')
        user = request.user

        ret, message = check_password_complexity(new_password, tenant)
        if not ret:
            return JsonResponse(
                data={
                    'error': Code.PASSWORD_STRENGTH_ERROR.value,
                    'message': message,
                }
            )
        if not user.check_password(old_password):
            return JsonResponse(
                data={
                    'error': Code.OLD_PASSWORD_ERROR.value,
                    'message': _('old password error'),
                }
            )
        if user.valid_password(new_password) is True:
            return JsonResponse(
                data={
                    'error': Code.PASSWORD_CHECK_ERROR.value,
                    'message': _('password is already in use'),
                }
            )
        user.set_password(new_password)
        user.save()
        return JsonResponse(data={'error': Code.OK.value})


@extend_schema(
    roles=['generaluser', 'tenantadmin', 'globaladmin'],
    tags=['user'],
    parameters=[
        OpenApiParameter(
            name='tenant_uuid',
            type={'type': 'string'},
            location=OpenApiParameter.PATH,
            required=True,
        )
    ],
)
class ResetPasswordView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, ApiAccessPermission]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = ResetPasswordRequestSerializer

    @extend_schema(
        roles=['tenantadmin', 'globaladmin'],
        responses=PasswordSerializer,
        summary='重置用户密码'
    )
    def post(self, request):
        tenant_uuid = self.request.query_params.get('tenant_uuid')
        if not tenant_uuid:
            tenant = None
        else:
            tenant = Tenant.valid_objects.filter(uuid=tenant_uuid).first()
        uuid = request.data.get('uuid', '')
        password = request.data.get('password', '')
        user = User.objects.filter(uuid=uuid).first()
        is_succeed = True
        if not user:
            return JsonResponse(
                data={
                    'error': Code.USER_EXISTS_ERROR.value,
                    'message': _('user does not exist'),
                }
            )
        if password:
            ret, message = check_password_complexity(password, tenant)
            if not ret:
                return JsonResponse(
                    data={
                        'error': Code.PASSWORD_STRENGTH_ERROR.value,
                        'message': message,
                    }
                )
        if password and user.valid_password(password) is True:
            return JsonResponse(
                data={
                    'error': Code.PASSWORD_CHECK_ERROR.value,
                    'message': _('password is already in use'),
                }
            )
        try:
            user.set_password(password)
            user.save()
        except Exception as e:
            is_succeed = False
        return Response(is_succeed)


@extend_schema(
    roles=['generaluser', 'tenantadmin', 'globaladmin'],
    tags=['user'],
    parameters=[
        OpenApiParameter(
            name='tenant_uuid',
            type={'type': 'string'},
            location=OpenApiParameter.QUERY,
            required=False,
        )
    ],
    summary='用户信息修改',
)
class UserInfoView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, ApiAccessPermission]
    authentication_classes = [ExpiringTokenAuthentication]
    serializer_class = UserInfoSerializer

    def get_object(self):
        return self.request.user

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['tenant_uuid'] = self.request.query_params.get('tenant_uuid', '')
        return context

    @extend_schema(summary='用户信息获取', roles=['generaluser', 'tenantadmin', 'globaladmin'])
    def get(self, request, *args, **kwargs):
        return super(UserInfoView, self).get(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        email = request.data.get('email')
        if email and not re.match(
            r'^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$',
            email,
        ):
            return JsonResponse(
                data={
                    'error': Code.EMAIL_FROMAT_ERROR.value,
                    'message': _('email format error'),
                }
            )
        mobile = request.data.get('mobile')
        if mobile and not re.match(r'(^(1)\d{10}$)', mobile):
            return JsonResponse(
                data={
                    'error': Code.MOBILE_FROMAT_ERROR.value,
                    'message': _('mobile format error'),
                }
            )
        return super(UserInfoView, self).update(request, *args, **kwargs)


@extend_schema(tags=['user'])
class UserBindInfoView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, ApiAccessPermission]
    authentication_classes = [ExpiringTokenAuthentication]
    serializer_class = UserBindInfoSerializer

    @extend_schema(
        roles=['generaluser', 'tenantadmin', 'globaladmin'],
        responses=UserBindInfoSerializer,
        summary='用户绑定信息'
    )
    def get(self, request):
        # 所有登录创建
        user = request.user
        result = []
        external_idps = ExternalIdp.valid_objects.order_by('order_no', 'id')
        available_extensions = find_available_extensions()
        for external_idp in external_idps:
            idp_type = external_idp.type
            for extension in available_extensions:
                extension_name = extension.name
                if idp_type == extension_name:
                    try:
                        items = extension.get_unbind_url(user)
                        if len(items) > 0:
                            for item in items:
                                result.append(item)
                    except:
                        print('没有启用插件，无法读取:'+extension_name)
        return JsonResponse({'data': result}, safe=False)


@extend_schema(tags=['user'])
class UserLogoutView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, ApiAccessPermission]
    authentication_classes = [ExpiringTokenAuthentication]

    @extend_schema(
        roles=['generaluser', 'tenantadmin', 'globaladmin'],
        responses=LogoutSerializer,
        summary='用户登出'
    )
    def get(self, request):
        user = request.user
        is_succeed = False
        if user and user.username:
            from rest_framework.authtoken.models import Token

            Token.objects.filter(user=user).delete()
            is_succeed = True
        return Response({"is_succeed": is_succeed})


@extend_schema(tags=['user'])
class UserLogoffView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, ApiAccessPermission]
    authentication_classes = [ExpiringTokenAuthentication]

    @extend_schema(
        roles=['generaluser', 'tenantadmin', 'globaladmin'],
        responses=UserLogoffSerializer,
        summary='用户注销',
    )
    def get(self, request):
        user = request.user
        User.objects.filter(id=user.id).delete()
        return Response({"is_succeed": True})

@extend_schema(tags=['user'])
class UserFreezeView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, ApiAccessPermission]
    authentication_classes = [ExpiringTokenAuthentication]

    @extend_schema(
        roles=['generaluser', 'tenantadmin', 'globaladmin'],
        responses=UserFreezeSerializer,
        summary='用户冻结',
    )
    def post(self, request, id):
        user = User.valid_objects.filter(uuid=id).first()
        is_active = request.date.get("is_active")
        user.is_active = is_active
        user.save()
        return Response({"is_succeed": True})

    @extend_schema(
        roles=['generaluser', 'tenantadmin', 'globaladmin'],
        responses=UserFreezeSerializer,
        summary='用户冻结',
    )
    def get(self, request, id):
        user = User.valid_objects.filter(uuid=id).first()
        return Response({"is_active": user.is_active})
@extend_schema(tags=['user'])
class UserTokenExpireView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, ApiAccessPermission]
    authentication_classes = [ExpiringTokenAuthentication]

    @extend_schema(
        roles=['generaluser', 'tenantadmin', 'globaladmin'],
        responses=UserTokenExpireSerializer,
        summary='用户token更新',
    )
    def get(self, request):
        user = request.user
        return Response({"token": user.new_token})


@extend_schema(tags=['user'])
class UserManageTenantsView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, ApiAccessPermission]
    authentication_classes = [ExpiringTokenAuthentication]

    @extend_schema(
        roles=['generaluser', 'tenantadmin', 'globaladmin'],
        responses=UserManageTenantsSerializer,
        summary='用户管理的租户',
    )
    def get(self, request):
        user = request.user
        if user and user.username:
            return Response(
                {
                    "manage_tenants": user.manage_tenants(),
                    "is_global_admin": user.is_superuser,
                    "is_platform_user": user.is_platform_user,
                }
            )


@extend_schema(tags=['user'])
class InviteUserCreateAPIView(generics.CreateAPIView):
    '''
    invite user
    '''

    permission_classes = [IsAuthenticated, ApiAccessPermission]
    authentication_classes = [ExpiringTokenAuthentication]

    @extend_schema(
        roles=['generaluser', 'tenantadmin', 'globaladmin'],
        summary='邀请用户',
    )
    def post(self, request, username):  # pylint: disable=arguments-differ
        data = request.data if request.data else {}

        inviter = request.user
        invitee = User.valid_objects.filter(username=username).first()
        if not invitee:
            raise ValidationError({'invitee': ['this user not exists']})

        # if invitee.is_settled:
        #     raise ValidationError({'invitee': ['this user has been settled']})

        # 之前的邀请即刻过期
        invitations = Invitation.valid_objects.filter(invitee=invitee, inviter=inviter)
        invitations.update(duration=datetime.timedelta(seconds=0))

        invitation = Invitation.active_objects.create(invitee=invitee, inviter=inviter)

        duration_minutes = data.get('duration_minutes', 0)
        if duration_minutes:
            invitation.duration = datetime.timedelta(minutes=duration_minutes)
            invitation.save()

        return Response(
            {
                'uuid': invitation.uuid.hex,
                'inviter': inviter.username,
                'invitee': invitee.username,
                'key': invitation.key,
                'expired_time': invitation.expired_time,
            }
        )


@extend_schema(
    roles=['tenantadmin', 'globaladmin', 'authmanage.permissionmanage'],
    tags=['user'],
    summary='分组用户列表',
)
class UserListAPIView(generics.ListAPIView):

    permission_classes = [IsAuthenticated, ApiAccessPermission]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = UserListSerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        tenant_uuid = self.kwargs['tenant_uuid']

        group = self.request.query_params.get('group', None)

        kwargs = {
            'tenants__uuid': tenant_uuid,
        }

        if group is not None:
            kwargs['groups__uuid__in'] = group.split(',')

        qs = User.valid_objects.filter(**kwargs).order_by('id')
        return qs