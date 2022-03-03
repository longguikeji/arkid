import json
import io
import datetime
from django.db import models
from django.http import Http404
from django.http.response import JsonResponse
from django.utils.translation import gettext_lazy as _
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
from inventory.models import User, Invitation, UserAppData, UserTenantPermissionAndPermissionGroup
from inventory.resouces import UserResource
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
    UserAppDataSerializer,
    UserLogoffSerializer,
    UserTokenExpireSerializer,
    UserListSerializer,
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
        context = self.get_serializer_context()
        tenant = context['tenant']

        support_content_types = [
            'application/csv',
            'text/csv',
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
        imported_data = dataset.load(
            io.StringIO(upload.read().decode('utf-8')), format='csv'
        )
        result = user_resource.import_data(
            dataset, dry_run=True, tenant_id=tenant.id
        )  # Test the data import
        for item in dataset:
            email = str(item[2])
            mobile = str(item[3])
            if email and not re.match(
                r'^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$',
                email,
            ):
                return JsonResponse(
                    data={
                        'error': Code.EMAIL_FROMAT_ERROR.value,
                        'message': _('email format error:{}'.format(email)),
                    }
                )
            if mobile and not re.match(r'(^(1)\d{10}$)', mobile):
                return JsonResponse(
                    data={
                        'error': Code.MOBILE_FROMAT_ERROR.value,
                        'message': _('mobile format error:{}'.format(mobile)),
                    }
                )
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
        roles=['tenantadmin', 'globaladmin', 'usermanage.userlist'],
        responses={(200, 'application/octet-stream'): OpenApiTypes.BINARY},
        summary='导出用户',
    )
    @action(detail=False, methods=['get'])
    def user_export(self, request, *args, **kwargs):
        context = self.get_serializer_context()
        tenant = context['tenant']

        kwargs = {
            'tenants__in': [tenant],
        }
        qs = User.active_objects.filter(**kwargs).order_by('id')
        data = UserResource().export(qs)
        export_data = data.csv
        content_type = 'application/octet-stream'
        response = HttpResponse(export_data, content_type=content_type)
        date_str = datetime.datetime.now().strftime('%Y-%m-%d')
        filename = '%s-%s.%s' % ('User', date_str, 'csv')
        response['Content-Disposition'] = 'attachment; filename="%s"' % (filename)
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
        return objs


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
        userAppData = UserAppData.active_objects.filter(user=self.request.user).first()
        if not userAppData:
            userAppData = UserAppData()
            userAppData.user = self.request.user
            userAppData.data = []
            userAppData.save()
        return userAppData


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
        uuid = request.data.get('uuid', '')
        password = request.data.get('password', '')
        old_password = request.data.get('old_password', '')
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

        if password and user.check_password(old_password) is False:
            return JsonResponse(
                data={
                    'error': Code.OLD_PASSWORD_ERROR.value,
                    'message': _('old password error'),
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
    roles=['tenantadmin', 'globaladmin'],
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