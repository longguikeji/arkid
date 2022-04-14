from django.http.response import JsonResponse
from rest_framework.views import APIView
from config import get_app_config
from openapi.utils import extend_schema
from api.v1.serializers.setup import (
    FrontendUrlSerializer,
)


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
        url = get_app_config().get_frontend_host()
        return JsonResponse({
            'url': url
        }, safe=False)
