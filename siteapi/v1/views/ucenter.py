'''
views for user center
面向普通用户开放
'''
import requests
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_403_FORBIDDEN, HTTP_200_OK
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import AnonymousUser

from drf_expiring_authtoken.views import ObtainExpiringAuthToken
from siteapi.v1.serializers.user import (
    UserWithPermSerializer,
    UserProfileSerializer,
)
from siteapi.v1.serializers.ucenter import (
    UserRegisterSerializer,
    SetPasswordSerializer,
    UserAlterMobileSerializer,
    UserInvitedProfileSerializer,
    UserContactSerializer,
)
from executer.core import CLI
from executer.log.rdb import LOG_CLI
from oneid_meta.models import Perm, User, DingConfig, Invitation, Group, APP, OAuthAPP
from thirdparty_data_sdk.dingding.dingsdk.accesstoken_manager import AccessTokenManager


class SetPasswordAPIView(generics.UpdateAPIView):
    '''
    用户重置密码
    - 短信
    - 旧密码
    '''

    permission_classes = []
    authentication_classes = []

    serializer_class = SetPasswordSerializer

    def get_object(self):
        return AnonymousUser()

    def perform_update(self, serializer):
        super().perform_update(serializer)
        LOG_CLI(serializer.instance).user_reset_password()


class UserContactAPIView(generics.UpdateAPIView):
    '''
    用户联系方式
    - 手机号
    - 私人邮箱
    '''

    permission_classes = [IsAuthenticated]

    serializer_class = UserContactSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object(), data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.validated_data)


class TokenPermAuthView(generics.RetrieveAPIView):
    '''
    校验token所代表的用户是否有某特定权限
    '''
    permission_classes = [
        IsAuthenticated,
    ]
    serializer_class = UserWithPermSerializer

    def get_serializer_context(self):
        '''
        add app to serializer_context if provided
        '''
        context = super().get_serializer_context()
        app_uid = self.request.query_params.get('app_uid', None)
        oauth_client_id = self.request.query_params.get('oauth_client_id', None)
        if app_uid:
            app = APP.valid_objects.filter(uid=app_uid).first()
            if not app:
                raise ValidationError({'app_uid': 'not exists'})
            context.update(app=app)
        if oauth_client_id:
            oauth_app = OAuthAPP.objects.filter(client_id=oauth_client_id).first()
            if not oauth_app:
                raise ValidationError({'oauth_clien_id': 'not exists'})
            if oauth_app.app:
                context.update(app=oauth_app.app)
        return context

    def get(self, request, *args, **kwargs):
        '''
        校验token所代表的用户是否有某特定权限
        - 默认的DEFAULT_AUTHENTICATION_CLASSES首先检查token有效性
        - 内部再校验token所代表的用户是否有某特定权限
        若未指定权限，则只检查token有效性
        '''
        user = request.user

        perm_uid = self.request.query_params.get('perm_uid', None)
        if perm_uid is None or user.is_admin:
            has_perm = True
        else:
            has_perm = user.has_perm(Perm.valid_objects.filter(uid=perm_uid).first())

        return Response(self.get_serializer(user).data, status=HTTP_200_OK if has_perm else HTTP_403_FORBIDDEN)


class InvitationKeyAuthView(generics.CreateAPIView):
    '''
    校验注册邀请码
    '''
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        '''
        校验注册邀请码是否有效
        '''
        key = request.data.get('key', '')
        if not key:
            raise ValidationError({'key': ['this field is requied']})

        mobile = request.data.get('mobile', '')
        if not mobile:
            raise ValidationError({'mobile': ['this field is requied']})

        invitation = Invitation.parse(key)
        if invitation is None:
            return Response({'key': ['invalid']}, status=status.HTTP_400_BAD_REQUEST)

        if invitation.is_expired:
            return Response({'key': ['expired']}, status=status.HTTP_400_BAD_REQUEST)

        if invitation.invitee.mobile != mobile:
            return Response({'mobile': ['invalid']}, status=status.HTTP_400_BAD_REQUEST)

        user = invitation.invitee
        return Response({
            'token': user.token,
            **UserWithPermSerializer(user).data,
        })


class UcenterProfileInvitedAPIView(generics.RetrieveUpdateAPIView):
    '''
    被邀请人的身份信息 [GET], [PATCH]
    '''

    permission_classes = []

    serializer_class = UserInvitedProfileSerializer

    def get(self, request, *args, **kwargs):
        key = request.query_params.get('key', '')
        if not key:
            raise ValidationError({'key': ['this field is requied']})

        invitation = Invitation.parse(key)
        if invitation is None:
            return Response({'key': ['invalid']}, status=status.HTTP_400_BAD_REQUEST)

        if invitation.is_expired:
            return Response({'key': ['expired']}, status=status.HTTP_400_BAD_REQUEST)

        user = invitation.invitee
        return Response({
        # 'token': user.token,
            **UserWithPermSerializer(user).data,
        })

    def update(self, request, *args, **kwargs):    # pylint: disable=unused-argument
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        user = validated_data.pop('user')
        if user.is_settled:
            raise AuthenticationFailed({'only for unsettled user'})
        cli = CLI(user=user)
        user.__dict__.update(validated_data)
        user.save()
        cli.set_user_password(user, validated_data['password'])
        LOG_CLI(user).user_activate()
        return Response({
        # 'token': user.token,
            **UserWithPermSerializer(user).data,
        })


class UserLoginAPIView(ObtainExpiringAuthToken):
    '''
    get token for user
    '''
    def attachment(self, token):
        user = token.user
        return UserWithPermSerializer(user).data


class UserRegisterAPIView(generics.CreateAPIView):
    '''
    create user with mobile
    '''

    permission_classes = []
    authentication_classes = []

    serializer_class = UserRegisterSerializer
    read_serializer_class = UserWithPermSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if 'private_email' in serializer.validated_data:
            user.origin = 4
        if 'mobile' in serializer.validated_data:
            user.origin = 3
        user.save()

        cli = CLI(user)
        cli.add_users_to_group([user], Group.get_extern_root())
        data = self.read_serializer_class(user).data
        data.update(token=user.token)
        return Response(data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        super().perform_create(serializer.instance)
        LOG_CLI(serializer.instance).user_register()


class DingLoginAPIView(generics.GenericAPIView):
    '''
    login by Ding Code
        https://open-doc.dingtalk.com/microapp/dev/about
        https://open-doc.dingtalk.com/microapp/serverapi2/clotub
    '''

    permission_classes = []
    authentication_classes = []

    def post(self, request):    # pylint: disable=no-self-use
        '''
        get oneid token by ding code
        '''
        code = request.data.get('code', None)
        if not code:
            raise ValidationError({'code': ['this field is requried']})

        ding_userid = self.auth_code(code)
        user = User.valid_objects.filter(ding_user__uid=ding_userid).first()
        if not user:
            raise ValidationError({'code': ["this account hasn't registered"]})

        res = UserWithPermSerializer(user).data
        res.update(token=user.token)

        LOG_CLI(user).user_login()

        return Response(data=res)

    def auth_code(self, code):
        '''
        get ding_userid by ding code
        '''
        res = requests.get("https://oapi.dingtalk.com/user/getuserinfo",
                           params={
                               "access_token": self.get_access_token(),
                               "code": code,
                           }).json()
        if res['errcode'] == 0:
            return res['userid']

        raise ValidationError({'code': ['invalid code']})

    @staticmethod
    def get_access_token():
        '''
        get ding api access token
        '''
        ding_config = DingConfig.get_current()
        token_manager = AccessTokenManager(
            app_key=ding_config.app_key,
            app_secret=ding_config.app_secret,
        )
        return token_manager.get_access_token()


class UcenterProfileAPIView(generics.RetrieveUpdateAPIView):
    '''
    get or update self profile
    '''

    permission_classes = [IsAuthenticated]

    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user


class UcenterMobileAPIView(generics.UpdateAPIView):
    '''
    update user mobile
    deprecated
    '''

    permission_classes = [IsAuthenticated]

    serializer_class = UserAlterMobileSerializer

    def get_object(self):
        return self.request.user


class RevokeTokenView(APIView):
    '''
    revoke token
    '''
    permission_classes = [IsAuthenticated]

    def post(self, request):    # pylint: disable=no-self-use
        '''
        user logout
        delete token
        '''
        user = request.user
        user.invalidate_token()
        return Response()
