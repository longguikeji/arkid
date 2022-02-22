import json
import io
import datetime
from inventory.models import Group
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
        roles=['tenantadmin', 'globaladmin'],
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
    ),
    create=extend_schema(
        roles=['tenantadmin', 'globaladmin'],
        request=GroupCreateRequestSerializer,
        responses=GroupSerializer,
    ),
    retrieve=extend_schema(
        roles=['tenantadmin', 'globaladmin'],
        responses=GroupSerializer,
    ),
    update=extend_schema(
        roles=['tenantadmin', 'globaladmin'],
        request=GroupSerializer,
        responses=GroupSerializer,
    ),
    destroy=extend_schema(
        roles=['tenantadmin', 'globaladmin'],
    ),
    partial_update=extend_schema(
        roles=['tenantadmin', 'globaladmin'],
    ),
)
@extend_schema(tags=['group'])
class GroupViewSet(BaseViewSet):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    model = Group

    serializer_class = GroupSerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        user = self.request.user
        context = self.get_serializer_context()
        tenant = context['tenant']
        check_result = user.check_permission(tenant)
        if not check_result is None:
            return []
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
        if tenant.has_admin_perm(user) is False:
            childmanager = ChildManager.valid_objects.filter(tenant=tenant, user=user).first()
            if childmanager:
                # 所在分组 所在分组的下级分组 指定分组与账号
                manager_visible = childmanager.manager_visible
                uuids = []
                if '所在分组' in manager_visible:
                    for group in user.groups.all():
                        uuids.append(group.uuid_hex)
                if '所在分组的下级分组' in manager_visible:
                    for group in user.groups.all():
                        group_uuids = []
                        group.child_groups(group_uuids)
                        uuids.extend(group_uuids)
                if '指定分组与账号' in manager_visible:
                    assign_group = childmanager.assign_group
                    uuids.extend(assign_group)
                qs = qs.filter(uuid__in=uuids)
        return qs.order_by('id')

    def get_object(self):
        context = self.get_serializer_context()
        tenant = context['tenant']
        user = self.request.user
        check_result = user.check_permission(tenant)
        if not check_result is None:
            return check_result
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
        user = self.request.user
        check_result = user.check_permission(tenant)
        if not check_result is None:
            return check_result

        group = self.get_object()

        # 删除相应的权限
        Permission.valid_objects.filter(
            tenant=instance.tenant,
            app=None,
            permission_category='数据',
            is_system_permission=True,
            group_info=group,
        ).delete()

        ret = super().destroy(request, *args, **kwargs)
        transaction.on_commit(lambda: WebhookManager.group_deleted(tenant.uuid, group))
        return ret

    @extend_schema(
        roles=['tenantadmin', 'globaladmin'],
        request=GroupImportSerializer,
        responses=GroupImportSerializer,
    )
    @action(detail=False, methods=['post'])
    def group_import(self, request, *args, **kwargs):
        context = self.get_serializer_context()
        tenant = context['tenant']
        user = request.user
        check_result = user.check_permission(tenant)
        if not check_result is None:
            return check_result

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
        roles=['tenantadmin', 'globaladmin'],
        responses={(200, 'application/octet-stream'): OpenApiTypes.BINARY},
    )
    @action(detail=False, methods=['get'])
    def group_export(self, request, *args, **kwargs):
        context = self.get_serializer_context()
        tenant = context['tenant']
        user = request.user
        check_result = user.check_permission(tenant)
        if not check_result is None:
            return check_result

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
