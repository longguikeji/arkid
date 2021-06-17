
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
        return self.runtime.authcode_provider.get_authcode_picture(request)


@extend_schema(tags=['authcode'])
class AuthCodeCheckView(generics.CreateAPIView):

    serializer_class = AuthCodeSerializer

    @property
    def runtime(self):
        return get_app_runtime()

    @extend_schema(
        responses=AuthCodeCheckResponseSerializer
    )
    def post(self, request):
        code = request.session.get('verification_code', None)
        check_code = request.data.get('code')
        if code and str(code).upper() == str(check_code).upper():
            return JsonResponse(data={
                'is_succeed': 0
            })
        else:
            return JsonResponse(data={
                'is_succeed': 1
            })
