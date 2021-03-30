from api.v1.views import user
from django.http import Http404
from django.http.response import JsonResponse
from rest_framework import generics, viewsets
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
import random
import string
from openapi.utils import extend_schema

from tenant.models import (
    Tenant,
)
from api.v1.serializers.login import LoginSerializer
from common.paginator import DefaultListPaginator
from runtime import get_app_runtime
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from rest_framework.authtoken.models import Token
from common.code import Code


@extend_schema(tags = ['sms'])
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
