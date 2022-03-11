from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.mixins import ListModelMixin
from rest_framework.generics import GenericAPIView
from rest_framework_extensions.settings import extensions_api_settings

from tenant.models import Tenant
from django.db.models import Q
from inventory.models import Permission, PermissionGroup, Group, UserTenantPermissionAndPermissionGroup

import re

class BaseAccessPermission:

    TEANT_STRING = extensions_api_settings.DEFAULT_PARENT_LOOKUP_KWARG_NAME_PREFIX + 'tenant'

    '''
    base权限验证类
    '''

    def get_operation_id(self, request, view):
        from django.contrib.admindocs.views import simplify_regex
        path_regex = request.resolver_match.route
        path_re = re.compile(
            r'<(?:(?P<converter>[^>:]+):)?(?P<parameter>\w+)>'
        )
        path = simplify_regex(path_regex)
        path = re.sub(path_re, r'{\g<parameter>}', path)
        path = path.replace('\\.', '.')
        # 获取operation_id
        tokenized_path = self._tokenize_path(path)
        tokenized_path = [t.replace('-', '_') for t in tokenized_path]
        method = request.method.lower()
        method_mapping = {
            'get': 'retrieve',
            'post': 'create',
            'put': 'update',
            'patch': 'partial_update',
            'delete': 'destroy',
        }
        action = ''
        if method == 'get' and self._is_list_view(method, path, view):
            action = 'list'
        else:
            action = method_mapping[method]

        if not tokenized_path:
            tokenized_path.append('root')

        if re.search(r'<drf_format_suffix\w*:\w+>', path_regex):
            tokenized_path.append('formatted')

        return '_'.join(tokenized_path + [action])

    def _tokenize_path(self, path):
        from drf_spectacular.settings import spectacular_settings
        path = re.sub(
            pattern=spectacular_settings.SCHEMA_PATH_PREFIX,
            repl='',
            string=path,
            flags=re.IGNORECASE
        )
        # remove path variables
        path = re.sub(pattern=r'\{[\w\-]+\}', repl='', string=path)
        # cleanup and tokenize remaining parts.
        path = path.rstrip('/').lstrip('/').split('/')
        return [t for t in path if t]

    def _is_list_view(self, method, path, view):
        import uritemplate

        from drf_spectacular.plumbing import (
            is_list_serializer, is_basic_type, error,
        )
        serializer = self.get_serializer_info(view)
        if isinstance(serializer, dict) and serializer:
            # extract likely main serializer from @extend_schema override
            serializer = {str(code): s for code, s in serializer.items()}
            serializer = serializer[min(serializer)]

        if is_list_serializer(serializer):
            return True
        if is_basic_type(serializer):
            return False
        if hasattr(view, 'action'):
            return view.action == 'list'
        # list responses are "usually" only returned by GET
        if method != 'get':
            return False
        if isinstance(view, ListModelMixin):
            return True
        # primary key/lookup variable in path is a strong indicator for retrieve
        if isinstance(view, GenericAPIView):
            lookup_url_kwarg = view.lookup_url_kwarg or view.lookup_field
            if lookup_url_kwarg in uritemplate.variables(path):
                return False
        return False

    def get_serializer_info(self, view):
        from drf_spectacular.plumbing import error
        try:
            if isinstance(view, GenericAPIView):
                # try to circumvent queryset issues with calling get_serializer. if view has NOT
                # overridden get_serializer, its safe to use get_serializer_class.
                if view.__class__.get_serializer == GenericAPIView.get_serializer:
                    return view.get_serializer_class()()
                return view.get_serializer()
            elif isinstance(view, APIView):
                # APIView does not implement the required interface, but be lenient and make
                # good guesses before giving up and emitting a warning.
                if callable(getattr(view, 'get_serializer', None)):
                    return view.get_serializer()
                elif callable(getattr(view, 'get_serializer_class', None)):
                    return view.get_serializer_class()()
                elif hasattr(view, 'serializer_class'):
                    return view.serializer_class
                else:
                    error(
                        'unable to guess serializer. This is graceful '
                        'fallback handling for APIViews. Consider using GenericAPIView as view base '
                        'class, if view is under your control. Ignoring view for now. '
                    )
            else:
                error('Encountered unknown view base class. Please report this issue. Ignoring for now')
        except Exception as exc:
            error(
                f'exception raised while getting serializer. Hint: '
                f'Is get_serializer_class() returning None or is get_queryset() not working without '
                f'a request? Ignoring the view for now. (Exception: {exc})'
            )

class ApiAccessPermission(BaseAccessPermission, permissions.BasePermission):

    def has_permission(self, request, view):
        operation_id = self.get_operation_id(request, view)
        tenant = None
        tenant_uuid = None
        # 租户uuid的所有可能的取值情况
        if self.TEANT_STRING in view.kwargs:
            tenant_uuid = view.kwargs[self.TEANT_STRING]
        if 'tenant_uuid' in view.kwargs:
            tenant_uuid = view.kwargs['tenant_uuid']
        if tenant_uuid is None:
            tenant_uuid = request.query_params.get('tenant', None)
        if tenant_uuid is None:
            tenant_uuid = request.query_params.get('tenant_uuid', None)
        # 给附租户
        if tenant_uuid:
            tenant = Tenant.objects.filter(uuid=tenant_uuid).first()
        user = request.user
        # permission = Permission.valid_objects.filter(
        #     is_system_permission=True,
        #     permission_category='API',
        #     operation_id=operation_id
        # ).first()
        permission = Permission.objects.raw("select id from inventory_permission where is_del = 0 and is_system_permission=1 and permission_category=%s and operation_id = %s limit 1", ['API', operation_id])
        if permission:
            permission = permission[0]
        else:
            permission = None
        if permission:
            # 用户权限分组
            permissiongroups = PermissionGroup.valid_objects.filter(
                permissions=permission
            )
            # 当前用户所拥有的权限分组
            user_permission_groups = []
            if tenant:
                # user_permission_groups = UserTenantPermissionAndPermissionGroup.valid_objects.filter(
                #     user=user,
                #     tenant=tenant
                # )
                user_permission_groups = UserTenantPermissionAndPermissionGroup.objects.raw("select * from inventory_usertenantpermissionandpermissiongroup where is_del=0 and tenant_id=%s and user_id=%s", [tenant.id, user.id])
            user_permissions_groups = []
            user_permissions = []
            for user_permission_group in user_permission_groups:
                # 权限分组
                if user_permission_group.permissiongroup is not None:
                    user_permissions_groups.append(user_permission_group.permissiongroup)
                # 权限
                if user_permission_group.permission is not None:
                    user_permissions.append(user_permission_group.permission)
            permissions_groups_ids = []
            for permissiongroup in permissiongroups:
                en_name = permissiongroup.en_name
                if en_name == 'generaluser':
                    # 普通用户
                    return True
                if en_name == 'globaladmin' and user.is_superuser:
                    # 超级管理员
                    return True
                if en_name == 'tenantadmin' and tenant and tenant.has_admin_perm(user):
                    # 租户管理员
                    return True
                for user_permissions_group in user_permissions_groups:
                    if user_permissions_group.id == permissiongroup.id:
                        return True
                # 数据补充
                permissions_groups_ids.append(permissiongroup.id)
            # 用户权限
            for user_permission in user_permissions:
                if user_permission.id == permission.id:
                    return True
            # 用户组权限
            groups = user.groups.filter(tenant=tenant).all()
            group_ids = []
            for group in groups:
                # 本体
                group_ids.append(group.id)
                # 父分组
                group.parent_groups(group_ids)
            if group_ids:
                return Group.valid_objects.filter(
                    Q(permissions=permission)|Q(permissions_groups__id__in=permissions_groups_ids),
                    id__in=group_ids
                ).exists()
        return False

    