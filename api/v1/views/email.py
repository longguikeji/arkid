'''
views for email
- send email
- check email_token
'''

from rest_framework.generics import GenericAPIView
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework import status
from openapi.utils import extend_schema
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from api.v1.serializers.email import (
    RegisterEmailClaimSerializer,
    ResetPWDEmailClaimSerializer,
    UserActivateEmailClaimSerializer,
    UpdateEmailEmailClaimSerializer,
)
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from common.code import Code

# from oneid_meta.models import AccountConfig


class EmailClaimAPIView(GenericAPIView):
    '''
    email api
    面向普通用户
    '''

    permission_classes = []
    authentication_classes = [ExpiringTokenAuthentication]

    def get_permissions(self):
        '''
        仅当重置私人邮箱时需要登录
        '''
        if self.kwargs.get('subject') == 'update_email':
            return [IsAuthenticated()]
        return []

    def get_authenticators(self):
        '''
        仅当重置私人邮箱时需要登录
        '''
        if self.kwargs.get('subject', '') in ('update_email',):
            return super().get_authenticators()
        return []

    def get_serializer_class(self):
        # account_config = AccountConfig.get_current()
        subject = self.kwargs['subject']

        if subject == 'register':
            # if not account_config.support_email_register:
            #     raise ValidationError({'email': ['unsupported']})
            return RegisterEmailClaimSerializer

        if subject == 'reset_password':
            # if not account_config.support_email:
            #     raise ValidationError({'email': ['unsupported']})
            return ResetPWDEmailClaimSerializer

        if subject == 'activate_user':
            # if not account_config.support_email:
            #     raise ValidationError({'email': ['unsupported']})
            return UserActivateEmailClaimSerializer

        if subject == 'update_email':
            # if not account_config.support_email:
            #     raise ValidationError({'email': ['unsupported']})
            return UpdateEmailEmailClaimSerializer

        raise NotFound

    @extend_schema(summary='发送邮件', roles=['tenantadmin', 'globaladmin', 'generaluser'])
    def post(self, request, *args, **kwargs):  # pylint: disable=unused-argument
        '''
        send email
        '''
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'error': Code.OK.value, 'message': 'email has send'},
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(summary='检查邮件token', roles=['tenantadmin', 'globaladmin', 'generaluser'])
    def get(self, request, *args, **kwarg):  # pylint: disable=unused-argument
        '''
        check email token
        '''
        email_token = request.query_params.get('email_token', '')
        if not email_token:
            raise ValidationError({'email_token': ['this field is required']})

        res = self.get_serializer().check_email_token(email_token)
        return Response(res)
