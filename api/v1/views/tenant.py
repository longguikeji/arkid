import urllib
from django.http.response import JsonResponse, HttpResponse
from django.utils.translation import gettext_lazy as _
from rest_framework.decorators import action
from rest_framework import generics
from openapi.utils import extend_schema
from rest_framework.response import Response
from app.models import App
from tenant.models import (
    Tenant,
    TenantConfig,
    TenantContactsConfig,
    TenantContactsUserFieldConfig,
    TenantContactsGroupConfig,
    TenantDesktopConfig,
    TenantLogConfig,
    TenantSwitch,
)

from api.v1.serializers.tenant import (
    TenantSerializer,
    TenantConfigSerializer,
    TenantContactsConfigFunctionSwitchSerializer,
    TenantContactsConfigInfoVisibilitySerializer,
    TenantContactsConfigGroupVisibilitySerializer,
    ContactsGroupSerializer,
    ContactsUserSerializer,
    TenantContactsUserTagsSerializer,
    TenantDesktopConfigSerializer,
    TenantCheckPermissionSerializer,
    TenantLogConfigSerializer,
    TenantSwitchSerializer,
    TenantSwitchInfoSerializer,
    TenantUserRoleSerializer,
    TenantCollectInfoSerializer,
    TenantUserPermissionSerializer,
)
from api.v1.serializers.app import AppBaseInfoSerializer
from api.v1.serializers.sms import RegisterSMSClaimSerializer, LoginSMSClaimSerializer
from api.v1.serializers.email import RegisterEmailClaimSerializer
from common.paginator import DefaultListPaginator
from common.native_field import NativeFieldNames
from drf_spectacular.openapi import OpenApiTypes
from runtime import get_app_runtime
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from rest_framework.authtoken.models import Token
from inventory.models import CustomField, Group, User, UserPassword, CustomUser, Permission, UserTenantPermissionAndPermissionGroup
from common.code import Code
from .base import BaseViewSet, BaseTenantViewSet
from app.models import App
from rest_framework.permissions import IsAuthenticated, AllowAny
from extension_root.childmanager.models import ChildManager
from drf_spectacular.utils import extend_schema_view
from perm.custom_access import ApiAccessPermission
from django.urls import reverse
from common import loginpage as lp
from config import get_app_config


@extend_schema_view(
    retrieve=extend_schema(roles=['generaluser', 'tenantadmin', 'globaladmin', 'tenantset.tenantconfig'], summary='租户详情'),
    destroy=extend_schema(roles=['generaluser', 'tenantadmin', 'globaladmin', 'tenantset.tenantconfig'], summary='租户删除'),
    partial_update=extend_schema(
        roles=['generaluser', 'tenantadmin', 'globaladmin', 'tenantset.tenantconfig'], summary='租户修改'
    ),
)
@extend_schema(tags=['tenant'])
class TenantViewSet(BaseViewSet):

    permission_classes = [AllowAny]
    authentication_classes = [ExpiringTokenAuthentication]

    pagination_class = DefaultListPaginator

    def get_serializer_class(self):
        if self.action == 'apps':
            return AppBaseInfoSerializer
        if self.action == 'list':
            return TenantUserRoleSerializer
        return TenantSerializer

    @extend_schema(
        roles=['generaluser', 'tenantadmin', 'globaladmin', 'usermanage.tenantlist'],
        action_type='list',
        summary='租户列表'
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        result = self.check_tenant_permission()
        if result is not None:
            return result
        return super().destroy(request, *args, **kwargs)
    
    def check_tenant_permission(self):
        '''
        检查租户权限
        '''
        object = self.get_object()
        user = self.request.user
        if user is None:
            return JsonResponse(
                data={
                    'error': Code.TENANT_NO_ACCESS.value,
                    'message': _('tenant no access'),
                }
            )
        if user.is_superuser is False:
            tenant = user.tenants.filter(is_del=False, id=object.id).first()
            if tenant and tenant.has_admin_perm(user):
                pass
            else:
                return JsonResponse(
                    data={
                        'error': Code.TENANT_NO_ACCESS.value,
                        'message': _('tenant no access'),
                    }
                )
        return None

    @extend_schema(roles=['tenantadmin', 'globaladmin', 'tenantset.tenantconfig'], summary=_('租户修改'))
    def update(self, request, *args, **kwargs):
        result = self.check_tenant_permission()
        if result is not None:
            return result
        # 权限slug
        slug = request.data.get('slug')
        tenant_exists = (
            Tenant.active_objects.exclude(uuid=kwargs.get('pk'))
            .filter(slug=slug)
            .exists()
        )
        if tenant_exists:
            return JsonResponse(
                data={
                    'error': Code.SLUG_EXISTS_ERROR.value,
                    'message': _('slug already exists'),
                }
            )
        return super().update(request, *args, **kwargs)


    @extend_schema(roles=['tenantadmin', 'globaladmin', 'tenantset.tenantconfig'], summary=_('租户修改'))
    def patch(self, request, *args, **kwargs):
        result = self.check_tenant_permission()
        if result is not None:
            return result
        # 权限slug
        slug = request.data.get('slug')
        tenant_exists = (
            Tenant.active_objects.exclude(uuid=kwargs.get('pk'))
            .filter(slug=slug)
            .exists()
        )
        if tenant_exists:
            return JsonResponse(
                data={
                    'error': Code.SLUG_EXISTS_ERROR.value,
                    'message': _('slug already exists'),
                }
            )
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        roles=['generaluser', 'tenantadmin', 'globaladmin', 'tenantset.tenantconfig'],
        summary=_('租户创建'),
    )
    def create(self, request):
        slug = request.data.get('slug')
        tenant_exists = Tenant.active_objects.filter(slug=slug).exists()
        if tenant_exists:
            return JsonResponse(
                data={
                    'error': Code.SLUG_EXISTS_ERROR.value,
                    'message': _('slug already exists'),
                }
            )
        return super().create(request)

    def get_queryset(self):
        user = self.request.user
        if user and user.username != "":
            if user.is_superuser:
                tenants = Tenant.active_objects.all()
                for tenant in tenants:
                    tenant.role = '超级管理员'
            else:
                tenants = user.tenants.filter(is_del=False).all()
                for tenant in tenants:
                    try:
                        from extension_root.childmanager.models import ChildManager
                        if ChildManager.valid_objects.filter(tenant=tenant, user=user).exists():
                            tenant.role = '子管理员'
                            continue
                    except:
                        print('没安装子管理员模块')
                    if tenant.has_admin_perm(user):
                        tenant.role = '管理员'
                    else:
                        tenant.role = '普通用户'
            return tenants
        else:
            return []

    def get_object(self):
        uuid = self.kwargs['pk']
        return Tenant.active_objects.filter(uuid=uuid).order_by('id').first()

    @property
    def runtime(self):
        return get_app_runtime()

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def get_password_error_count(self, ip, check_str='login'):
        key = f'{ip}-{check_str}'
        if self.runtime.cache_provider is None:
            return 0
        data = self.runtime.cache_provider.get(key)
        if data is None:
            return 0
        return int(data)

    def mark_user_login_failed(self, ip, check_str='login'):
        key = f'{ip}-{check_str}'
        runtime = get_app_runtime()
        data = runtime.cache_provider.get(key)
        if data is None:
            v = 1
        else:
            v = int(data) + 1
        self.runtime.cache_provider.set(key, v, 86400)

    @action(detail=True, methods=['GET'])
    def apps(self, request, pk):
        user: User = request.user
        tenant: Tenant = self.get_object()

        all_apps = App.active_objects.filter(
            tenant=tenant,
        )

        if tenant.has_admin_perm(user) or user.is_superuser:
            objs = all_apps
        else:
            all_apps_perms = [app.access_perm_code for app in all_apps]

            perms = set(
                [
                    perm.permissions.codename
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

        serializer = self.get_serializer(objs, many=True)
        return Response(serializer.data)


@extend_schema(roles=['generaluser', 'tenantadmin', 'globaladmin'], tags=['tenant'], summary='获取租户slug')
class TenantSlugView(generics.RetrieveAPIView):

    serializer_class = TenantSerializer

    @extend_schema(responses=TenantSerializer)
    def get(self, request, slug):
        obj = Tenant.active_objects.filter(slug=slug).order_by('id').first()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)


@extend_schema(roles=['tenantadmin', 'globaladmin', 'authfactor.factorconfig'], tags=['tenant'])
class TenantConfigView(generics.RetrieveUpdateAPIView):

    permission_classes = [IsAuthenticated, ApiAccessPermission]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = TenantConfigSerializer

    def get_object(self):
        tenant_uuid = self.kwargs['tenant_uuid']
        tenant = Tenant.active_objects.filter(uuid=tenant_uuid).first()
        if tenant:
            tenantconfig, is_created = TenantConfig.objects.get_or_create(
                is_del=False,
                tenant=tenant,
            )
            if is_created:
                default_data = TenantConfigSerializer(tenantconfig).data
                tenantconfig.data = default_data.get('data')
                tenantconfig.save()
            return tenantconfig

    @extend_schema(
        roles=['tenantadmin', 'globaladmin', 'generaluser', 'authfactor.factorconfig'],
        summary='租户配置获取'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin', 'authfactor.factorconfig'],
        summary='租户配置更新'
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin', 'authfactor.factorconfig'],
        summary='租户配置更新'
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


@extend_schema(roles=['tenantadmin', 'globaladmin'], tags=['tenant'], summary='租户提示信息数')
class TenantCollectInfoView(generics.RetrieveAPIView):

    permission_classes = [IsAuthenticated, ApiAccessPermission]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = TenantCollectInfoSerializer

    @extend_schema(responses=TenantCollectInfoSerializer)
    def get(self, request, tenant_uuid):
        tenant = Tenant.active_objects.filter(uuid=tenant_uuid).first()
        app_count = App.active_objects.filter(tenant=tenant).count()
        user_count = User.active_objects.filter(tenants__in=[tenant]).count()
        message_count = 0
        dict_item = {
            'message_count': message_count,
            'app_count': app_count,
            'user_count': user_count,
        }
        serializer = self.get_serializer(dict_item)
        return Response(serializer.data)




@extend_schema(roles=['tenantadmin', 'globaladmin'], tags=['tenant'])
class TenantContactsConfigFunctionSwitchView(generics.RetrieveUpdateAPIView):

    permission_classes = [IsAuthenticated, ApiAccessPermission]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = TenantContactsConfigFunctionSwitchSerializer

    def get_object(self):
        tenant_uuid = self.kwargs['tenant_uuid']
        return TenantContactsConfig.active_objects.filter(
            tenant__uuid=tenant_uuid
        ).first()

    @extend_schema(
        roles=['tenantadmin', 'globaladmin', 'generaluser'],
        summary='租户通讯录开关获取'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin', 'userset.contactsset'],
        summary='租户通讯录开关修改'
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin', 'userset.contactsset'],
        summary='租户通讯录开关修改'
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


@extend_schema(roles=['tenantadmin', 'globaladmin'], tags=['tenant'])
class TenantContactsConfigInfoVisibilityDetailView(generics.RetrieveUpdateAPIView):

    permission_classes = [IsAuthenticated, ApiAccessPermission]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = TenantContactsConfigInfoVisibilitySerializer

    def get_object(self):
        tenant_uuid = self.kwargs['tenant_uuid']
        info_uuid = self.kwargs['info_uuid']
        return TenantContactsUserFieldConfig.active_objects.filter(
            tenant__uuid=tenant_uuid, uuid=info_uuid
        ).first()

    @extend_schema(
        roles=['tenantadmin', 'globaladmin'],
        summary='租户通讯录个人字段详情'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin'],
        summary='租户通讯录个人字段修改'
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin'],
        summary='租户通讯录个人字段修改'
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


@extend_schema(roles=['tenantadmin', 'globaladmin', 'userset.contactsset'], tags=['tenant'], summary='租户通讯录个人字段列表')
class TenantContactsConfigInfoVisibilityView(generics.ListAPIView):

    permission_classes = [IsAuthenticated, ApiAccessPermission]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = TenantContactsConfigInfoVisibilitySerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        tenant_uuid = self.kwargs['tenant_uuid']

        return TenantContactsUserFieldConfig.active_objects.filter(
            tenant__uuid=tenant_uuid
        ).order_by('-id')


@extend_schema(roles=['tenantadmin', 'globaladmin'], tags=['tenant'])
class TenantContactsConfigGroupVisibilityView(generics.RetrieveUpdateAPIView):

    permission_classes = [IsAuthenticated, ApiAccessPermission]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = TenantContactsConfigGroupVisibilitySerializer

    def get_object(self):
        tenant_uuid = self.kwargs['tenant_uuid']
        group_uuid = self.kwargs['group_uuid']
        group_config = TenantContactsGroupConfig.active_objects.filter(
            tenant__uuid=tenant_uuid, group__uuid=group_uuid
        ).first()
        if group_config:
            return group_config
        else:
            tenant = Tenant.active_objects.filter(uuid=tenant_uuid).first()
            group = Group.active_objects.filter(uuid=group_uuid).first()
            group_config = TenantContactsGroupConfig()
            group_config.tenant = tenant
            group_config.group = group
            group_config.data = {
                "visible_type": "所有人可见",
                "visible_scope": [],
                "assign_group": [],
                "assign_user": [],
            }
            group_config.save()
            return group_config

    @extend_schema(
        roles=['tenantadmin', 'globaladmin', 'userset.contactsset'],
        summary='租户通讯录分组配置详情'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin', 'userset.contactsset'],
        summary='租户通讯录分组配置修改'
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin', 'userset.contactsset'],
        summary='租户通讯录分组配置修改'
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


@extend_schema(roles=['generaluser', 'tenantadmin', 'globaladmin'], tags=['tenant'], summary='租户通讯录分组配置列表')
class TenantContactsGroupView(generics.ListAPIView):

    permission_classes = [IsAuthenticated, ApiAccessPermission]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = ContactsGroupSerializer
    pagination_class = DefaultListPaginator

    def get_switch(self, tenant_uuid):
        # 功能开关
        # {
        #     "is_open": true
        # }
        config = TenantContactsConfig.active_objects.filter(
            tenant__uuid=tenant_uuid
        ).first()
        return config.data

    def get_group_visible(self, tenant_uuid):
        configs = TenantContactsGroupConfig.active_objects.filter(
            tenant__uuid=tenant_uuid
        )
        return configs

    def get_queryset(self):

        parent = self.request.query_params.get('parent', None)
        user = self.request.user
        tenant = Tenant.active_objects.filter(uuid=self.kwargs['tenant_uuid']).first()

        kwargs = {
            'tenant__uuid': self.kwargs['tenant_uuid'],
        }
        if parent is None:
            kwargs['parent'] = None
        else:
            kwargs['parent__uuid'] = parent
        qs = Group.valid_objects.filter(**kwargs)
        if tenant.has_admin_perm(user) is False:
            # 功能开关
            switch = self.get_switch(self.kwargs['tenant_uuid'])
            is_open = switch.get('is_open', True)
            if is_open is False:
                return []
            # 分组可见性
            configs = self.get_group_visible(self.kwargs['tenant_uuid'])
            uuids = []
            for group in qs:
                group_config = configs.filter(group=group).first()
                if group_config:
                    group_visible = group_config.data
                    visible_type = group_visible.get('visible_type', '所有人可见')
                    if visible_type == '部分人可见':
                        visible_scope = group_visible.get('visible_scope', [])
                        if visible_scope:
                            # 组内成员可见 下属分组可见 指定分组与人员
                            if '组内成员可见' in visible_scope:
                                if user.groups.filter(uuid=group.uuid_hex).exists():
                                    uuids.append(str(group.uuid_hex))
                                    continue
                            if '下属分组可见' in visible_scope:
                                # 取得当前分组的所有下属分组
                                group_uuids = []
                                group.child_groups(group_uuids)
                                if user.groups.filter(uuid__in=group_uuids).exists():
                                    uuids.append(str(group.uuid_hex))
                                    continue
                            if '指定分组与人员' in visible_scope:
                                assign_group = group_visible.get('assign_group', [])
                                assign_user = group_visible.get('assign_user', [])
                                if assign_group and user.groups.filter(uuid__in=assign_group).exists():
                                    uuids.append(str(group.uuid_hex))
                                    continue
                                elif assign_user and str(user.uuid_hex) in assign_user:
                                    uuids.append(str(group.uuid_hex))
                                    continue
                    else:
                        uuids.append(str(group.uuid_hex))
                else:
                    uuids.append(str(group.uuid_hex))
            qs = qs.filter(uuid__in=uuids)
            return qs.order_by('id')
            # visible_type = group_visible.get('visible_type', '所有人可见')
            # if visible_type == '部分人可见':
            #     visible_scope = group_visible.get('visible_scope', [])
            #     if visible_scope:
            #         # 组内成员可见 下属分组可见 指定分组与人员
            #         groups = user.groups
            #         uuids = []
            #         if '组内成员可见' in visible_scope:
            #             for group in groups:
            #                 uuid = group.uuid_hex
            #                 if uuid not in uuids:
            #                     uuids.append(uuid)
            #         if '下属分组可见' in visible_scope:
            #             # 递归查询(下下级不筛选)
            #             if not parent:
            #                 # 如果是一级，就只能看到下属分组
            #                 child_groups = Group.valid_objects.filter(parent__in=groups)
            #                 for child_group in child_groups:
            #                     uuid = child_group.uuid_hex
            #                     if uuid not in uuids:
            #                         uuids.append(uuid)
            #             else:
            #                 # 如果是二级，就不进行筛选
            #                 uuids = []
            #         if '指定分组与人员' in visible_scope:
            #             assign_group = group_visible.get('assign_group', [])
            #             for uuid in assign_group:
            #                 if uuid not in uuids:
            #                     uuids.append(uuid)
            #         if uuids:
            #             kwargs['uuid__in'] = uuids
            #     else:
            #         if parent is None:
            #             if len(visible_scope) == 1 and '下属分组可见' in visible_scope:
            #                 pass
            #             else:
            #                 kwargs['parent'] = None
            #         else:
            #             kwargs['parent__uuid'] = parent
            # else:
            #     if parent is None:
            #         kwargs['parent'] = None
            #     else:
            #         kwargs['parent__uuid'] = parent
        else:
            return qs


@extend_schema(roles=['generaluser', 'tenantadmin', 'globaladmin'], tags=['tenant'], summary='租户通讯录用户列表')
class TenantContactsUserView(generics.ListAPIView):

    permission_classes = [IsAuthenticated, ApiAccessPermission]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = ContactsUserSerializer
    pagination_class = DefaultListPaginator

    def get_switch(self, tenant_uuid):
        # 功能开关
        # {
        #     "is_open": true
        # }
        config = TenantContactsConfig.active_objects.filter(
            tenant__uuid=tenant_uuid
        ).first()
        return config.data

    def get_queryset(self):

        group_uuid = self.request.query_params.get('group_uuid', None)
        user = self.request.user
        tenant = Tenant.active_objects.filter(uuid=self.kwargs['tenant_uuid']).first()
        kwargs = {
            'tenants__uuid': self.kwargs['tenant_uuid'],
            'groups__uuid': group_uuid,
        }
        if tenant.has_admin_perm(user) is False:
            # 功能开关
            switch = self.get_switch(self.kwargs['tenant_uuid'])
            is_open = switch.get('is_open', True)
            if is_open is False:
                return []
        qs = User.valid_objects.filter(**kwargs).order_by('id')
        # 需要对结果集进行一些处理
        dict_item = {
            '用户名': 'username',
            '姓名': 'nickname',
            '电话': 'mobile',
            '邮箱': 'email',
            '职位': 'job_title',
        }
        configs = TenantContactsUserFieldConfig.active_objects.filter(tenant=tenant)
        myself_field = []
        manager_field = []
        part_field = []
        current_user_field = []
        all_user_field = []
        for config in configs:
            data = config.data
            visible_type = data.get('visible_type')
            visible_scope = data.get('visible_scope')
            assign_user = data.get('assign_user')
            assign_group = data.get('assign_group')
            item_name = dict_item.get(config.name)
            if visible_type == '所有人可见':
                all_user_field.append(item_name)
            else:
                if visible_type == '部分人可见' and '本人可见' in visible_scope:
                    myself_field.append(item_name)
                if visible_type == '部分人可见' and '管理员可见' in visible_scope:
                    manager_field.append(item_name)
                    if (
                        tenant.has_admin_perm(user) is True
                        and item_name not in current_user_field
                    ):
                        current_user_field.append(item_name)
                if visible_type == '部分人可见' and '指定分组与人员' in visible_scope:
                    part_field.append(item_name)
                    # 和用户身份挂钩
                    if user.uuid_hex in assign_user:
                        current_user_field.append(item_name)
                    else:
                        groups = user.groups
                        for group in groups:
                            uuid = group.uuid
                            if (
                                uuid in assign_group
                                and item_name not in current_user_field
                            ):
                                current_user_field.append(item_name)
        for item in qs:
            if (
                'username' not in all_user_field
                and 'username' not in current_user_field
            ):
                if 'username' in myself_field and item.uuid_hex == user.uuid_hex:
                    pass
                else:
                    item.username = ''
            if (
                'nickname' not in all_user_field
                and 'nickname' not in current_user_field
            ):
                if 'nickname' in myself_field and item.uuid_hex == user.uuid_hex:
                    pass
                else:
                    item.nickname = ''
            if 'mobile' not in all_user_field and 'mobile' not in current_user_field:
                if 'mobile' in myself_field and item.uuid_hex == user.uuid_hex:
                    pass
                else:
                    item.mobile = ''
            if 'email' not in all_user_field and 'email' not in current_user_field:
                if 'email' in myself_field and item.uuid_hex == user.uuid_hex:
                    pass
                else:
                    item.email = ''
            if (
                'job_title' not in all_user_field
                and 'job_title' not in current_user_field
            ):
                if 'job_title' in myself_field and item.uuid_hex == user.uuid_hex:
                    pass
                else:
                    item.job_title = ''
        return qs


@extend_schema(roles=['generaluser', 'tenantadmin', 'globaladmin'], tags=['tenant'], summary='租户通讯录用户字段列表', responses=TenantContactsUserTagsSerializer)
class TenantContactsUserTagsView(generics.RetrieveAPIView):

    serializer_class = TenantContactsUserTagsSerializer

    def get(self, request, tenant_uuid):
        tenant = Tenant.active_objects.filter(uuid=tenant_uuid).first()
        dict_item = {
            '用户名': 'username',
            '姓名': 'nickname',
            '电话': 'mobile',
            '邮箱': 'email',
            '职位': 'job_title',
        }
        configs = TenantContactsUserFieldConfig.active_objects.filter(tenant=tenant)
        myself_field = []
        manager_field = []
        part_field = []
        all_user_field = []
        for config in configs:
            data = config.data
            visible_type = data.get('visible_type')
            visible_scope = data.get('visible_scope')
            item_name = dict_item.get(config.name)
            if visible_type == '所有人可见':
                all_user_field.append(item_name)
            else:
                if visible_type == '部分人可见' and '本人可见' in visible_scope:
                    myself_field.append(item_name)
                if visible_type == '部分人可见' and '管理员可见' in visible_scope:
                    manager_field.append(item_name)
                if visible_type == '部分人可见' and '指定分组与人员' in visible_scope:
                    part_field.append(item_name)

        serializer = self.get_serializer(
            {
                'myself_field': myself_field,
                'manager_field': manager_field,
                'part_field': part_field,
                'all_user_field': all_user_field,
            }
        )
        return Response(serializer.data)


@extend_schema(roles=['tenantadmin', 'globaladmin'], tags=['tenant'])
class TenantDesktopConfigView(generics.RetrieveUpdateAPIView):

    permission_classes = [IsAuthenticated, ApiAccessPermission]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = TenantDesktopConfigSerializer

    def get_object(self):
        tenant_uuid = self.kwargs['tenant_uuid']
        tenant = Tenant.active_objects.get(uuid=tenant_uuid)

        config = TenantDesktopConfig.active_objects.filter(tenant=tenant).first()
        if config is None:
            config = TenantDesktopConfig()
            config.tenant = tenant
            config.data = {'access_with_desktop': True, 'icon_custom': True}
            config.save()
        return config

    @extend_schema(
        roles=['tenantadmin', 'globaladmin', 'generaluser'],
        summary='租户桌面配置详情'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin', 'userset.desktopset'],
        summary='租户桌面配置修改'
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin', 'userset.desktopset'],
        summary='租户桌面配置修改'
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


@extend_schema(
    roles=['generaluser', 'tenantadmin', 'globaladmin'],
    tags=['tenant'],
    responses=TenantCheckPermissionSerializer,
    summary='租户检查权限'
)
class TenantCheckPermissionView(generics.RetrieveAPIView):

    permission_classes = [IsAuthenticated, ApiAccessPermission]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = TenantCheckPermissionSerializer

    def get(self, request, tenant_uuid):
        user = request.user
        childmanager = None
        try:
            from extension_root.childmanager.models import ChildManager
            childmanager = ChildManager.valid_objects.filter(tenant__uuid=tenant_uuid, user=user).first()
        except:
            print('没安装子管理员模块')
        result = {}
        if childmanager:
            result['is_childmanager'] = True
            if childmanager.manager_permission == '全部权限':
                result['is_all_show'] = True
                result['is_all_application'] = False
                result['permissions'] = []
            elif childmanager.manager_permission == '所有应用权限':
                result['is_all_show'] = False
                result['is_all_application'] = True
                result['permissions'] = []
            else:
                result['is_all_show'] = False
                result['is_all_application'] = False
                assign_permission = childmanager.assign_permission_uuid
                if len(assign_permission) != 0:
                    permissions = Permission.valid_objects.filter(uuid__in=assign_permission)
                    items = []
                    for permission in permissions:
                        items.append({
                            'uuid': permission.uuid_hex,
                            'codename': permission.codename,
                            'is_system_permission': permission.is_system_permission,
                            'name': permission.name,
                            'permission_category': permission.permission_category,
                        })
                    result['permissions'] = items
                else:
                    result['permissions'] = []
        else:
            result['is_all_application'] = False
            result['is_childmanager'] = False
            result['is_all_show'] = False
            result['permissions'] = []
        serializer = self.get_serializer(result)
        return Response(serializer.data)


@extend_schema(
    roles=['generaluser', 'tenantadmin', 'globaladmin'],
    tags=['tenant'],
    responses=TenantUserPermissionSerializer,
    summary='当前用户在当前租户拥有的权限'
)
class TenantUserPermissionView(generics.RetrieveAPIView):

    permission_classes = [IsAuthenticated, ApiAccessPermission]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = TenantUserPermissionSerializer

    def get(self, request, tenant_uuid):
        # 用户
        user = request.user
        is_superuser = user.is_superuser
        # 租户
        tenant = Tenant.objects.get(uuid=tenant_uuid)
        is_tenantadmin = tenant.has_admin_perm(user)
        en_names = []
        if is_superuser is False and is_tenantadmin is False:
            # 用户权限组
            user_permissions_groups = []
            user_permission_group_infos = UserTenantPermissionAndPermissionGroup.valid_objects.filter(
                permissiongroup__isnull=False,
                user=user,
                tenant=tenant
            )
            for user_permission_group_info in user_permission_group_infos:
                user_permissions_groups.append(user_permission_group_info.permissiongroup)
            for user_permissions_group in user_permissions_groups:
                if user_permissions_group.en_name:
                    en_names.append(user_permissions_group.en_name)
            # 用户所属分组的权限组
            groups = user.groups.filter(tenant=tenant).all()
            group_ids = []
            for group in groups:
                # 本体
                group_ids.append(group.id)
                # 父分组
                group.parent_groups(group_ids)
            if group_ids:
                groups = Group.valid_objects.filter(
                    id__in=group_ids
                )
                for group in groups:
                    permissions_groups = group.permissions_groups.all()
                    for permissions_group in permissions_groups:
                        if permissions_group.en_name:
                            en_names.append(permissions_group.en_name)
        result = {
            'is_globaladmin': is_superuser,
            'is_tenantadmin': is_tenantadmin,
            'en_names': en_names,
            'global_en_names': [
                'pluginmanage.pluginconfig',
                'pluginmanage.pluginstore',
                'platformmanage.bindplatform',
                'platformmanage.platformconfig'
            ]
        }
        serializer = self.get_serializer(result)
        return Response(serializer.data)


@extend_schema(roles=['tenantadmin', 'globaladmin'], tags=['tenant'])
class TenantLogConfigView(generics.RetrieveUpdateAPIView):

    permission_classes = [IsAuthenticated, ApiAccessPermission]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = TenantLogConfigSerializer

    def get_object(self):
        tenant_uuid = self.kwargs['tenant_uuid']
        tenant = Tenant.objects.filter(uuid=tenant_uuid).first()

        log_config, is_created = TenantLogConfig.objects.get_or_create(
            is_del=False,
            tenant=tenant,
        )
        frontend_host = get_app_config().get_frontend_host()
        path = f'/api/v1/tenant/{tenant_uuid}/log'
        url = urllib.parse.urljoin(frontend_host, path)

        data = log_config.data
        if is_created is True:
            data['log_api'] = url
            data['log_retention_period'] = 30
        else:
            data['log_api'] = url
            if 'log_retention_period' not in data:
                data['log_retention_period'] = 30

        log_config.save()
        return log_config

    @extend_schema(
        roles=['tenantadmin', 'globaladmin'],
        summary='租户日志配置详情'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin'],
        summary='租户日志配置修改'
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin'],
        summary='租户日志配置修改'
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


@extend_schema(roles=['globaladmin', 'platformmanage.platformconfig'], tags=['tenant'])
class TenantSwitchView(generics.RetrieveUpdateAPIView):

    permission_classes = [IsAuthenticated, ApiAccessPermission]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = TenantSwitchSerializer

    def get_object(self):
        tenant_switch = TenantSwitch.active_objects.first()
        return tenant_switch

    @extend_schema(
        roles=['globaladmin', 'platformmanage.platformconfig'],
        summary='租户功能开关详情'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        roles=['globaladmin', 'platformmanage.platformconfig'],
        summary='租户功能开关修改'
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        roles=['globaladmin', 'platformmanage.platformconfig'],
        summary='租户功能开关修改'
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)



@extend_schema(roles=['generaluser','tenantadmin', 'globaladmin'], tags=['tenant'], summary='租户功能开关信息')
class TenantSwitchInfoView(generics.RetrieveAPIView):

    permission_classes = []
    authentication_classes = []

    serializer_class = TenantSwitchInfoSerializer

    def get(self, request):
        default_tenant = Tenant.objects.filter(id=1).first()
        if default_tenant:
            tenant_switch = TenantSwitch.active_objects.first()
            if not tenant_switch:
                tenant_switch = TenantSwitch()
                tenant_switch.tenant = default_tenant
                tenant_switch.switch = True
                tenant_switch.save()
        # 开关信息
        switch = tenant_switch.switch
        # default tenant
        tenant = Tenant.objects.filter(id=1).first()
        tenant_uuid = ''
        if tenant:
            tenant_uuid = tenant.uuid_hex
        data = {
            'switch': switch,
            'platform_tenant_uuid': tenant_uuid
        }
        serializer = self.get_serializer(data)
        return Response(serializer.data)
