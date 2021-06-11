import json
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
from django.http import HttpResponse, HttpResponseRedirect


@extend_schema_view(
    list=extend_schema(
        roles=['tenant admin', 'global admin'],
        responses=GroupSerializer,
        parameters=[
            OpenApiParameter(
                "parent",
                OpenApiTypes.UUID,
                OpenApiParameter.QUERY,
                description='group.uuid',
            ),
        ],
    ),
    create=extend_schema(
        roles=['tenant admin', 'global admin'],
        request=GroupCreateRequestSerializer,
        responses=GroupSerializer,
    ),
    retrieve=extend_schema(
        roles=['tenant admin', 'global admin'],
        responses=GroupSerializer,
    ),
    update=extend_schema(
        roles=['tenant admin', 'global admin'],
        request=GroupSerializer,
        responses=GroupSerializer,
    ),
    destroy=extend_schema(
        roles=['tenant admin', 'global admin'],
    ),
    partial_update=extend_schema(
        roles=['tenant admin', 'global admin'],
    ),
)
@extend_schema(tags=['group'])
class GroupViewSet(BaseViewSet):

    # permission_classes = [IsAuthenticated]
    # authentication_classes = [ExpiringTokenAuthentication]

    model = Group

    permission_classes = []
    authentication_classes = []

    serializer_class = GroupSerializer
    pagination_class = DefaultListPaginator


    def get_queryset(self):
        context = self.get_serializer_context()
        tenant = context['tenant']

        parent = self.request.query_params.get('parent', None)

        kwargs = {
            'tenant': tenant,
        }

        if parent is None:
            kwargs['parent'] = None
        else:
            kwargs['parent__uuid'] = parent

        qs = Group.valid_objects.filter(**kwargs).order_by('id')
        return qs


    def get_object(self):
        context = self.get_serializer_context()
        tenant = context['tenant']

        kwargs = {
            'tenant': tenant,
            'uuid': self.kwargs['pk'],
        }

        obj = Group.valid_objects.filter(**kwargs).first()
        return obj

    @extend_schema(
        roles=['tenant admin', 'global admin'],
        request=GroupImportSerializer,
        responses=GroupImportSerializer,
    )
    @action(detail=False, methods=['post'])
    def group_import(self, request, *args, **kwargs):
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
        user_resource = GroupResource()
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
        roles=['tenant admin', 'global admin'],
        responses={(200, 'application/octet-stream'): OpenApiTypes.BINARY},
    )
    @action(detail=False, methods=['get'])
    def group_export(self, request, *args, **kwargs):
        context = self.get_serializer_context()
        tenant = context['tenant']
        kwargs = {
            'tenant': tenant,
        }

        qs = Group.objects.filter(**kwargs).order_by('id')
        data = GroupResource().export(qs)
        export_data = data.xlsx
        content_type = 'application/octet-stream'
        response = HttpResponse(export_data, content_type=content_type)
        date_str = datetime.datetime.now().strftime('%Y-%m-%d')
        filename = '%s-%s.%s' % ('Group', date_str, 'xlsx')
        response['Content-Disposition'] = 'attachment; filename="%s"' % (filename)
        return response
