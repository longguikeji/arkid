from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from runtime import get_app_runtime
from openapi.utils import extend_schema
from api.v1.serializers.storage import UploadSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from django.utils.translation import gettext_lazy as _
from django.http.response import JsonResponse
from common.code import Code
from tenant.models import (
    Tenant, TenantConfig,
)


@extend_schema(tags = ['upload'], roles=['generaluser', 'tenantadmin', 'globaladmin'])
class UploadAPIView(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]
    serializer_class = UploadSerializer

    @property
    def storage_provider(self):
        r = get_app_runtime()

        storage_provider = r.storage_provider
        assert storage_provider is not None
        return storage_provider

    def post(self, request):
        if 'file' not in request.data:
            raise ParseError("Empty content")
        uploaded_file = request.data['file']
        tenant_uuid = request.data.get('tenant_uuid', '')
        # 扩展名称验证
        if tenant_uuid:
            result = self.get_upload_config(tenant_uuid)
            exts = result.get('upload_file_format', ['jpg','png','gif','jpeg'])
        else:
            exts = ['jpg','png','gif','jpeg']
        ext = str(uploaded_file.name.split('.')[-1]).lower()
        if ext not in exts:
            return JsonResponse(data={
                'error': Code.FILE_FROMAT_ERROR.value,
                'message': _('file format error'),
            })
        key = self.storage_provider.upload(uploaded_file)
        return Response(status=status.HTTP_201_CREATED, data={
            'key': key,
        })

    def get_upload_config(self, tenant_uuid):
        # 获取基础配置信息
        result = {
            'upload_file_format': ['jpg','png','gif','jpeg']
        }
        tenantconfig = TenantConfig.active_objects.filter(tenant__uuid=tenant_uuid).first()
        if tenantconfig:
            result = tenantconfig.data
        return result