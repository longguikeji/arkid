from django.http.response import JsonResponse
from rest_framework import generics
from django.utils.translation import gettext_lazy as _
from openapi.utils import extend_schema
from api.v1.serializers.authcode import (
    AuthCodeSerializer,
    AuthCodeResponseSerializer,
    AuthCodeCheckResponseSerializer,
)
from runtime import get_app_runtime
from common.code import Code
from login_register_config.models import OtherAuthFactor


@extend_schema(tags=['authcode'])
class AuthCodeGenerateView(generics.RetrieveAPIView):
    @property
    def runtime(self):
        return get_app_runtime()

    @extend_schema(responses=AuthCodeResponseSerializer)
    def get(self, request):
        provider_cls = self.runtime.other_auth_factor_providers.get('auth_code')
        if provider_cls is None:
            return JsonResponse(
                data={
                    'error': Code.AUTHCODE_PROVIDER_IS_MISSING.value,
                    'message': _('Please enable a authcode Provider extension'),
                }
            )
        config = OtherAuthFactor.valid_objects.filter(type='auth_code').first()
        if not config:
            config_data = {'auth_code_length': 4}
        else:
            config_data = config.data
        provider = provider_cls(config_data)
        key, char_4, base64_str = provider.get_authcode_picture()
        # 存当前验证码(验证码会缓存1天)
        self.runtime.cache_provider.set(key, char_4, 86400)
        return JsonResponse(data={'key': key, 'base64': str(base64_str, 'utf8')})


@extend_schema(tags=['authcode'])
class AuthCodeCheckView(generics.CreateAPIView):

    serializer_class = AuthCodeSerializer

    @property
    def runtime(self):
        return get_app_runtime()

    @extend_schema(responses=AuthCodeCheckResponseSerializer)
    def post(self, request):
        key = request.data.get('file_name')
        check_code = request.data.get('code')
        code = self.runtime.cache_provider.get(key)
        if code and str(code).upper() == str(check_code).upper():
            return JsonResponse(data={'is_succeed': 0})
        else:
            return JsonResponse(data={'is_succeed': 1})
