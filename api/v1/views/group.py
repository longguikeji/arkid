import json
import io
import datetime
from inventory.models import Group, UserTenantPermissionAndPermissionGroup
from api.v1.serializers.group import (
    GroupSerializer,
    GroupListResponseSerializer,
    GroupCreateRequestSerializer,
    GroupCreateResponseSerializer,
    GroupImportSerializer,
)
from common.paginator import DefaultListPaginator
from .base import BaseViewSet
from openapi.utils import extend_schema
from perm.custom_access import ApiAccessPermission
from drf_spectacular.utils import extend_schema_view, OpenApiParameter
from drf_spectacular.openapi import OpenApiTypes
from rest_framework.response import Response
from rest_framework.decorators import action
from inventory.resouces import GroupResource
from tablib import Dataset
from collections import defaultdict
from common.code import Code
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from extension_root.childmanager.models import ChildManager
from webhook.manager import WebhookManager
from django.db import transaction


@extend_schema_view(
    list=extend_schema(
        roles=['tenantadmin', 'globaladmin', 'generaluser', 'usermanage.groupmanage'],
        responses=GroupSerializer,
        parameters=[
            OpenApiParameter(
                "parent",
                OpenApiTypes.UUID,
                OpenApiParameter.QUERY,
                description='group.uuid',
                required=False,
            ),
            OpenApiParameter(
                name='name',
                type={'type': 'string'},
                location=OpenApiParameter.QUERY,
                required=False,
            ),
        ],
        summary='分组列表',
    ),
    create=extend_schema(
        roles=['tenantadmin', 'globaladmin', 'usermanage.groupmanage'],
        request=GroupCreateRequestSerializer,
        responses=GroupSerializer,
        summary='分组创建',
    ),
    retrieve=extend_schema(
        roles=['tenantadmin', 'globaladmin', 'generaluser', 'usermanage.groupmanage'],
        responses=GroupSerializer,
        summary='分组获取',
    ),
    update=extend_schema(
        roles=['tenantadmin', 'globaladmin', 'usermanage.groupmanage'],
        request=GroupSerializer,
        responses=GroupSerializer,
        summary='分组更新',
    ),
    destroy=extend_schema(
        roles=['tenantadmin', 'globaladmin', 'usermanage.groupmanage'],
        summary='分组删除',
    ),
    partial_update=extend_schema(
        roles=['tenantadmin', 'globaladmin', 'usermanage.groupmanage'],
        summary='分组更新',
    ),
)
@extend_schema(tags=['group'])
class GroupViewSet(BaseViewSet):

    permission_classes = [IsAuthenticated, ApiAccessPermission]
    authentication_classes = [ExpiringTokenAuthentication]

    model = Group

    serializer_class = GroupSerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        user = self.request.user
        context = self.get_serializer_context()
        tenant = context['tenant']

        # 分组
        parent = self.request.query_params.get('parent', None)
        name = self.request.query_params.get('name', None)

        kwargs = {
            'tenant': tenant,
        }

        if parent is None:
            kwargs['parent'] = None
        else:
            kwargs['parent__uuid'] = parent

        if name is not None:
            kwargs['name'] = name

        qs = Group.valid_objects.filter(**kwargs)
        # 用户
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
            if parent is not None:
                qs = qs.filter(id__in=group_ids)
            # childmanager = ChildManager.valid_objects.filter(tenant=tenant, user=user).first()
            # if childmanager:
            #     # 所在分组 所在分组的下级分组 指定分组与账号
            #     manager_visible = childmanager.manager_visible
            #     uuids = []
            #     if '所在分组' in manager_visible:
            #         for group in user.groups.all():
            #             uuids.append(group.uuid_hex)
            #     if '所在分组的下级分组' in manager_visible:
            #         for group in user.groups.all():
            #             group_uuids = []
            #             group.child_groups(group_uuids)
            #             uuids.extend(group_uuids)
            #     if '指定分组与账号' in manager_visible:
            #         assign_group = childmanager.assign_group
            #         uuids.extend(assign_group)
            #     qs = qs.filter(uuid__in=uuids)
        return qs.order_by('id')

    def get_object(self):
        context = self.get_serializer_context()
        tenant = context['tenant']
  
        kwargs = {
            'tenant': tenant,
            'uuid': self.kwargs['pk'],
        }

        obj = Group.valid_objects.filter(**kwargs).first()
        return obj

    @transaction.atomic()
    def destroy(self, request, *args, **kwargs):
        context = self.get_serializer_context()
        tenant = context['tenant']

        group = self.get_object()

        # 删除相应的权限
        ret = super().destroy(request, *args, **kwargs)
        transaction.on_commit(lambda: WebhookManager.group_deleted(tenant.uuid, group))
        return ret

    @extend_schema(
        roles=['tenantadmin', 'globaladmin'],
        request=GroupImportSerializer,
        responses=GroupImportSerializer,
        summary='分组导入',
    )
    @action(detail=False, methods=['post'])
    def group_import(self, request, *args, **kwargs):
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
                    'error': Code.GROUP_IMPORT_ERROR.value,
                    'message': 'No file find in form dada',
                }
            )
        if upload.content_type not in support_content_types:
            return Response(
                {
                    'error': Code.GROUP_IMPORT_ERROR.value,
                    'message': 'ContentType Not Support!',
                }
            )
        group_resource = GroupResource()
        dataset = Dataset()
        imported_data = dataset.load(
            io.StringIO(upload.read().decode('utf-8')), format='csv'
        )
        result = group_resource.import_data(
            dataset, dry_run=True, tenant_id=tenant.id
        )  # Test the data import
        if not result.has_errors() and not result.has_validation_errors():
            group_resource.import_data(dataset, dry_run=False, tenant_id=tenant.id)
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
                    'error': Code.GROUP_IMPORT_ERROR.value,
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
        roles=['tenantadmin', 'globaladmin', 'usermanage.groupmanage'],
        summary='分组导出',
        responses={(200, 'application/octet-stream'): OpenApiTypes.BINARY},
    )
    @action(detail=False, methods=['get'])
    def group_export(self, request, *args, **kwargs):
        context = self.get_serializer_context()
        tenant = context['tenant']

        kwargs = {
            'tenant': tenant,
        }

        qs = Group.active_objects.filter(**kwargs).order_by('id')
        data = GroupResource().export(qs)
        export_data = data.csv
        content_type = 'application/octet-stream'
        response = HttpResponse(export_data, content_type=content_type)
        date_str = datetime.datetime.now().strftime('%Y-%m-%d')
        filename = '%s-%s.%s' % ('Group', date_str, 'csv')
        response['Content-Disposition'] = 'attachment; filename="%s"' % (filename)
        return response
