'''
views for email
- send email
- check email_token
'''

from rest_framework.generics import GenericAPIView
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from infrastructure.serializers.email import (
    RegisterEmailClaimSerializer,
    ResetPWDEmailClaimSerializer,
    UserActivateEmailClaimSerializer,
    UpdateEmailEmailClaimSerializer,
)
from oneid_meta.models import AccountConfig


class EmailClaimAPIView(GenericAPIView):
    '''
    email api
    面向普通用户
    '''

    permission_classes = []

    def get_permissions(self):
        '''
        仅当重置私人邮箱时需要登录
        '''
        if self.kwargs['subject'] == 'update_email':
            return [IsAuthenticated()]
        return []

    def get_authenticators(self):
        '''
        仅当重置私人邮箱时需要登录
        '''
        if self.kwargs.get('subject', '') in ('update_email', ):
            return super().get_authenticators()
        return []

    def get_serializer_class(self):
        account_config = AccountConfig.get_current()
        subject = self.kwargs['subject']

        if subject == 'register':
            if not account_config.support_email_register:
                raise ValidationError({'email': ['unsupported']})
            return RegisterEmailClaimSerializer

        if subject == 'reset_password':
            if not account_config.support_email:
                raise ValidationError({'email': ['unsupported']})
            return ResetPWDEmailClaimSerializer

        if subject == 'activate_user':
            if not account_config.support_email:
                raise ValidationError({'email': ['unsupported']})
            return UserActivateEmailClaimSerializer

        if subject == 'update_email':
            if not account_config.support_email:
                raise ValidationError({'email': ['unsupported']})
            return UpdateEmailEmailClaimSerializer

        raise NotFound

    def post(self, request, *args, **kwargs):    # pylint: disable=unused-argument
        '''
        send email
        '''
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response('email has send', status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwarg):    # pylint: disable=unused-argument
        '''
        check email token
        '''
        email_token = request.query_params.get('email_token', '')
        if not email_token:
            raise ValidationError({'email_token': ['thid field is required']})

        res = self.get_serializer().check_email_token(email_token)
        return Response(res)
