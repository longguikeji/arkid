from django.http.response import JsonResponse
from rest_framework.views import APIView
from config import get_app_config
from openapi.utils import extend_schema
from api.v1.serializers.setup import (
    FrontendUrlSerializer,
)
from rest_framework.permissions import IsAuthenticated
from system.permission import IsSuperAdmin
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from config.models import PlatformConfig
from common.code import Code
from django.utils.translation import gettext_lazy as _


@extend_schema(
    summary='获取前端的url',
    roles=['generaluser', 'tenantadmin', 'globaladmin'],
    # responses=PasswordLoginResponseSerializer,
)
class GetFrontendUrlAPIView(APIView):
    permission_classes = []
    authentication_classes = []

    @extend_schema(responses=FrontendUrlSerializer)
    def get(self, request):
        # url = get_app_config().get_frontend_host()
        # return JsonResponse({
        #     'url': url
        # }, safe=False)
        url = ''
        plat_config = PlatformConfig.valid_objects.filter().first()
        if plat_config:
            url = plat_config.frontend_url
        return JsonResponse({
            'url': url
        }, safe=False)


class SetFrontendUrlAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    authentication_classes = [ExpiringTokenAuthentication]

    @extend_schema(responses=FrontendUrlSerializer)
    def post(self, request):
        # url = get_app_config().get_frontend_host()
        # return JsonResponse({
        #     'url': url
        # }, safe=False)
        url = request.data.get('url')
        if not url:
            return JsonResponse(
                data={
                    'error': Code.POST_DATA_ERROR.value,
                    'message': _('empty url value'),
                }
            )
        url = url.rstrip('/')
        plat_config = PlatformConfig.valid_objects.filter().first()
        if not plat_config:
            plat_config = PlatformConfig.valid_objects.create(frontend_url=url)
        else:
            plat_config.frontend_url = url
            plat_config.save()

        return JsonResponse(data={'error': Code.OK.value, 'data': {'url': url}})
