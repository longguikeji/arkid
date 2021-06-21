
from django.http.response import JsonResponse
from rest_framework import generics
from django.utils.translation import gettext_lazy as _
import random
import string
from openapi.utils import extend_schema

from api.v1.serializers.login import LoginSerializer
from common.paginator import DefaultListPaginator
from runtime import get_app_runtime
from common.code import Code


@extend_schema(tags = ['sms'], roles=['general user', 'tenant admin', 'global admin'])
class SendSMSView(generics.CreateAPIView):

    serializer_class = LoginSerializer
    pagination_class = DefaultListPaginator
    
    @property
    def runtime(self):
        return get_app_runtime()

    def create(self, request):
        mobile = request.data.get('mobile')

        if self.runtime.sms_provider is None:
            return JsonResponse(data={
                'error': Code.SMS_PROVIDER_IS_MISSING.value,
                'message': _('Please enable a SMS Provider extension'),
            })

        code = ''.join(random.choice(string.digits) for _ in range(6))

        self.runtime.cache_provider.set(mobile, code, 120)
        self.runtime.sms_provider.send_auth_code(mobile, code)

        return JsonResponse(data={
            'error': Code.OK.value,
        })
