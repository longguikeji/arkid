
from django.http.response import JsonResponse
from rest_framework import generics
from django.utils.translation import gettext_lazy as _
from openapi.utils import extend_schema
from api.v1.serializers.authcode import AuthCodeSerializer, AuthCodeResponseSerializer, AuthCodeCheckResponseSerializer
from runtime import get_app_runtime
from common.code import Code


@extend_schema(tags=['authcode'])
class AuthCodeGenerateView(generics.RetrieveAPIView):

    @property
    def runtime(self):
        return get_app_runtime()

    @extend_schema(
        responses=AuthCodeResponseSerializer
    )
    def get(self, request):

        if self.runtime.authcode_provider is None:
            return JsonResponse(data={
                'error': Code.AUTHCODE_PROVIDER_IS_MISSING.value,
                'message': _('Please enable a authcode Provider extension'),
            })
        if self.runtime.storage_provider is None:
            return JsonResponse(data={
                'error': Code.LOCAL_STORAGE_PROVIDER_IS_MISSING.value,
                'message': _('Please enable a local_storage Provider extension'),
            })
        char_4, key = self.runtime.authcode_provider.get_authcode_picture()
        # 存当前验证码
        print(char_4)
        print(key)
        self.runtime.cache_provider.set(key, char_4, 180)
        return JsonResponse(data={
            'key': key
        })


@ extend_schema(tags=['authcode'])
class AuthCodeCheckView(generics.CreateAPIView):

    serializer_class = AuthCodeSerializer

    @ property
    def runtime(self):
        return get_app_runtime()

    @extend_schema(
        responses=AuthCodeCheckResponseSerializer
    )
    def post(self, request):
        key = request.data.get('file_name')
        check_code = request.data.get('code')
        code = self.runtime.cache_provider.get(key)
        if code and str(code).upper() == str(check_code).upper():
            return JsonResponse(data={
                'is_succeed': 0
            })
        else:
            return JsonResponse(data={
                'is_succeed': 1
            })
