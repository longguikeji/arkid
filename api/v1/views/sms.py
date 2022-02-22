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
from rest_framework.permissions import IsAuthenticated
from api.v1.serializers.sms import (
    SMSClaimSerializer,
    ResetPWDSMSClaimSerializer,
    RegisterSMSClaimSerializer,
    LoginSMSClaimSerializer,
    UserActivateSMSClaimSerializer,
    UpdateMobileSMSClaimSerializer,
)
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from inventory.models import User
from rest_framework import status
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication


# @extend_schema(tags=['sms'], roles=['generaluser', 'tenantadmin', 'globaladmin'])
# class SendSMSView(generics.CreateAPIView):

#     serializer_class = LoginSerializer
#     pagination_class = DefaultListPaginator

#     @property
#     def runtime(self):
#         return get_app_runtime()

#     def create(self, request):
#         mobile = request.data.get('mobile')

#         if self.runtime.sms_provider is None:
#             return JsonResponse(
#                 data={
#                     'error': Code.SMS_PROVIDER_IS_MISSING.value,
#                     'message': _('Please enable a SMS Provider extension'),
#                 }
#             )

#         code = ''.join(random.choice(string.digits) for _ in range(6))

#         self.runtime.cache_provider.set(mobile, code, 120)
#         self.runtime.sms_provider.send_auth_code(mobile, code)

#         return JsonResponse(
#             data={
#                 'error': Code.OK.value,
#             }
#         )


@extend_schema(tags=['sms'], roles=['generaluser', 'tenantadmin', 'globaladmin'])
class SMSClaimAPIView(GenericAPIView):
    '''
    sms api
    面向普通用户

    未登录用户必须通过图片验证才能发短信
    已登录用户则无限制
    '''

    permission_classes = []
    authentication_classes = [ExpiringTokenAuthentication]

    def get_permissions(self):
        '''
        仅修改手机时需要登录
        '''
        if self.kwargs.get('subject', '') in ('update_mobile',):
            return [IsAuthenticated()]
        return []

    def get_authenticators(self):
        '''
        仅修改手机时需要登录
        '''
        if self.kwargs.get('subject', '') in ('update_mobile',):
            return super().get_authenticators()
        return []

    def get_serializer_class(self):
        if 'subject' not in self.kwargs:
            return SMSClaimSerializer

        # account_config = AccountConfig.get_current()
        subject = self.kwargs.get('subject')

        if subject == 'register':
            # if not account_config.support_mobile_register:
            #     raise ValidationError({'mobile': ['unsupported']})
            return RegisterSMSClaimSerializer

        # if not account_config.support_mobile:
        #     raise ValidationError({'mobile': ['unsupported']})

        if subject == 'reset_password':
            return ResetPWDSMSClaimSerializer

        if subject == 'activate_user':
            return UserActivateSMSClaimSerializer

        if subject == 'update_mobile':
            return UpdateMobileSMSClaimSerializer

        if subject == 'ding_bind':
            return SMSClaimSerializer

        if subject == 'login':
            return LoginSMSClaimSerializer

        raise NotFound

    def post(self, request, *args, **kwargs):  # pylint: disable=unused-argument
        '''
        send sms
        '''
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # 增加对mobile的检查，确定
        mobile = serializer.validated_data['mobile']

        return Response(
            {
                # 'isregister': User.valid_objects.filter(mobile=mobile).exists(),
                'error': Code.OK.value,
                'message': 'sms has send',
            },
            status=status.HTTP_201_CREATED,
        )

    def get(self, request, *args, **kwargs):  # pylint: disable=unused-argument
        '''
        check sms
        '''
        sms_token, expired = self.get_serializer().check_sms(request.query_params)
        return Response({'sms_token': sms_token, 'expired': expired})
