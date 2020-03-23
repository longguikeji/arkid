'''
views for sms
- send sms
- check sms
'''
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from infrastructure.serializers.sms import (
    ResetPWDSMSClaimSerializer,
    RegisterSMSClaimSerializer,
    UpdateMobileSMSClaimSerializer,
    UserActivateSMSClaimSerializer,
    SMSClaimSerializer,
    LoginSMSClaimSerializer,
)
from oneid_meta.models import AccountConfig


class SMSClaimAPIView(GenericAPIView):
    '''
    sms api
    面向普通用户

    未登录用户必须通过图片验证才能发短信
    已登录用户则无限制
    '''
    def get_permissions(self):
        '''
        仅修改手机时需要登录
        '''
        if self.kwargs.get('subject', '') in ('update_mobile', ):
            return [IsAuthenticated()]
        return []

    def get_authenticators(self):
        '''
        仅修改手机时需要登录
        '''
        if self.kwargs.get('subject', '') in ('update_mobile', ):
            return super().get_authenticators()
        return []

    def get_serializer_class(self):
        if 'subject' not in self.kwargs:
            return SMSClaimSerializer

        account_config = AccountConfig.get_current()
        subject = self.kwargs['subject']

        if subject == 'register':
            if not account_config.support_mobile_register:
                raise ValidationError({'mobile': ['unsupported']})
            return RegisterSMSClaimSerializer

        if not account_config.support_mobile:
            raise ValidationError({'mobile': ['unsupported']})

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

    def post(self, request, *args, **kwargs):    # pylint: disable=unused-argument
        '''
        send sms
        '''
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response('sms has send', status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):    # pylint: disable=unused-argument
        '''
        check sms
        '''
        sms_token, expired = self.get_serializer().check_sms(request.query_params)
        return Response({'sms_token': sms_token, 'expired': expired})
