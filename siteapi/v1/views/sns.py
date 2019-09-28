'''
扫码登录视图
'''
import requests

from rest_framework.generics import GenericAPIView
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_408_REQUEST_TIMEOUT)
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from drf_expiring_authtoken.models import ExpiringToken
from drf_expiring_authtoken.views import ObtainExpiringAuthToken

from siteapi.v1.serializers.user import UserWithPermSerializer
from siteapi.v1.serializers.ucenter import DingRegisterAndBindSerializer

from infrastructure.serializers.sms import SMSClaimSerializer

from executer.core import CLI
from executer.log.rdb import LOG_CLI

from oneid_meta.models import User, Group, DingUser, AccountConfig

from settings_local import SMS_CONFIG


class DingQrCallbackView(ObtainExpiringAuthToken):
    '''
    dingding/qr/callback/
    用戶扫码登录获取用户dingId，openid, unionId
    '''
    permission_classes = []
    authentication_classes = []

    appid = SMS_CONFIG['appid']
    appsecret = SMS_CONFIG['appsecret']
    baseurl = 'https://oapi.dingtalk.com/sns/'
    get_access_url = baseurl + 'gettoken'
    get_sns_url = baseurl + 'get_sns_token'
    get_persistent_code_url = baseurl + 'get_persistent_code'
    get_ding_info_url = baseurl + 'getuserinfo'

    def post(self, request, *args, **kwargs):
        '''
        处理钉钉用户扫码之后重定向到`首页`或`绑定页面`
        '''
        state = request.data.get('state')
        code = request.data.get('code')
        if state == 'STATE' and code != '':
            try:
                user_ids = self.get_ding_id(code)
            except RuntimeError:
                return Response('get dingding user time out', HTTP_408_REQUEST_TIMEOUT)
        else:
            return Response('get tmp code error', HTTP_400_BAD_REQUEST)
        ding_id = user_ids['dingId']
        ding_user = DingUser.valid_objects.filter(dingId=ding_id).first()
        if ding_user:
            user = User.valid_objects.filter(mobile=ding_user.mobile).first()
        else:
            user = False
        if user:
            token, _ = ExpiringToken.objects.get_or_create(user=user)
            if token.expired():
                token.delete()
                token = ExpiringToken.objects.create(user=user)
            context = {'token': token.key, **self.attachment(token)}
        else:
            context = {'token': '', 'dingId': ding_id}
            return Response(context, HTTP_200_OK)

    def attachment(self, token):
        '''
        登录用户
        '''
        user = token.user
        return UserWithPermSerializer(user).data

    def get_ding_id(self, code):
        '''
        从钉钉获取dingId
        '''
        access_token = requests.get(self.get_access_url, params={'appid':self.appid,\
            'appsecret':self.appsecret}).json()['access_token']
        get_psstt_code = requests.post(self.get_persistent_code_url, params={'access_token':access_token},\
        json={'tmp_auth_code':code})
        openid = get_psstt_code.json()['openid']
        persistent_code = get_psstt_code.json()['persistent_code']
        sns_token = requests.post(self.get_sns_url, params={'access_token':access_token},\
        json={'openid':openid, 'persistent_code':persistent_code}).json()['sns_token']
        user_info = requests.get(self.get_ding_info_url, params={'sns_token': sns_token}).json()['user_info']
        user_ids = {'dingId': user_info['dingId'], 'openid': user_info['openid'], 'unionid': user_info['unionid']}
        return user_ids


class DingBindSMSClaimAPIView(GenericAPIView):
    '''
    /ding/bind/sms/
    发送绑定验证短信
    '''
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = SMSClaimSerializer

    def get_permissions(self):
        '''
        仅修改手机时需要登录
        '''
        return []

    def get_serializer_class(self):
        account_config = AccountConfig.get_current()
        if not account_config.support_mobile:
            raise ValidationError({'mobile': ['unsupported']})
        return SMSClaimSerializer

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


class DingQueryUserAPIView(ObtainExpiringAuthToken, GenericAPIView):
    '''
    /ding/query/user/
    检查用户是否注册
    '''
    permission_classes = []
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        sms_token = request.data.get('sms_token', None)
        if sms_token:
            mobile = SMSClaimSerializer.check_sms_token(sms_token)['mobile']
            if isinstance(mobile, str):
                exist = User.valid_objects.filter(mobile=mobile).exists()
                return Response({'exist': exist})

        else:
            raise ValidationError({'sms_token': ["sms_token invalid"]})


class DingBindAPIView(ObtainExpiringAuthToken, GenericAPIView):
    '''
    /ding/bind/
    处理绑定
    '''
    permission_classes = []
    authentication_classes = []

    read_serializer_class = UserWithPermSerializer

    def post(self, request, *args, **kwargs):
        ding_id = request.data.get('dingId')
        sms_token = request.data.get('sms_token')
        mobile = SMSClaimSerializer.check_sms_token(sms_token)['mobile']
        print(mobile)
        user = User.valid_objects.filter(mobile=mobile).first()
        token, _ = ExpiringToken.objects.get_or_create(user=user)
        if token.expired():
            token.delete()
            token = ExpiringToken.objects.create(user=user)
        user.save()
        ding_user = DingUser.objects.filter(dingId=ding_id).first()
        if ding_user:
            ding_user.update({'mobile': mobile, 'user': user, 'id': user.id})
            ding_user.save()
        else:
            ding_user = DingUser.objects.create(dingId=ding_id, mobile=mobile, user=user, id=user.id)
            # , 'user': user, 'id': user.id
            ding_user.save()
        data = {'token': token.key, **self.attachment(token)}
        LOG_CLI(user).user_login()
        return Response(data, HTTP_201_CREATED)

    #     return Response(serializer.errors, HTTP_400_BAD_REQUEST)

    def attachment(self, token):
        user = token.user
        return UserWithPermSerializer(user).data


class DingRegisterAndBindView(generics.CreateAPIView):
    '''
    钉钉扫码用户注册页面
    '''
    permission_classes = []
    authentication_classes = []

    serializer_class = DingRegisterAndBindSerializer
    read_serializer_class = UserWithPermSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        mobile = serializer.validated_data['mobile']
        user.save()

        token, _ = ExpiringToken.objects.get_or_create(user=user)
        user.save()
        if token.expired():
            token.delete()
            token = ExpiringToken.objects.create(user=user)

        ding_id = serializer.validated_data['dingId']
        ding_user = DingUser.objects.filter(dingId=ding_id).first()
        if ding_user:
            ding_user.update({'mobile': mobile, 'user': user, 'id': user.id})
            ding_user.save()
        else:
            ding_user = DingUser.objects.create(dingId=ding_id, mobile=mobile, user=user, id=user.id)
            ding_user.save()
        cli = CLI(user)
        cli.add_users_to_group([user], Group.get_extern_root())
        data = self.read_serializer_class(user).data
        data.update(token=user.token)
        return Response(data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        super().perform_create(serializer.instance)
        LOG_CLI(serializer.instance).user_register()
