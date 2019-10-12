'''
扫码登录视图
'''
import requests

from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED,\
    HTTP_400_BAD_REQUEST, HTTP_408_REQUEST_TIMEOUT, HTTP_403_FORBIDDEN)
from rest_framework.response import Response

from siteapi.v1.serializers.user import UserWithPermSerializer
from siteapi.v1.serializers.ucenter import DingRegisterAndBindSerializer, DingBindSerializer

from infrastructure.serializers.sms import SMSClaimSerializer

from executer.core import CLI
from executer.log.rdb import LOG_CLI

from oneid_meta.models import User, Group, DingUser, DingConfig, AccountConfig


def require_ding_qr_supported(func):
    '''
    检查是否允许扫码登录装饰器
    '''
    def inner(self, request):
        return Response({'err_msg':'ding qr not allowed'}, HTTP_403_FORBIDDEN)\
            if not AccountConfig.get_current().support_ding_qr else func(self, request)
    return inner


class DingQrCallbackView(APIView):
    '''
    dingding/qr/callback/
    用戶扫码登录获取用户ding_id，openid, unionId
    '''
    permission_classes = []
    authentication_classes = []
    baseurl = 'https://oapi.dingtalk.com/sns/'
    get_access_url = baseurl + 'gettoken'
    get_sns_url = baseurl + 'get_sns_token'
    get_persistent_code_url = baseurl + 'get_persistent_code'
    get_ding_info_url = baseurl + 'getuserinfo'

    @require_ding_qr_supported
    def post(self, request):
        '''
        处理钉钉用户扫码之后重定向到‘首页’或‘绑定页面’
        '''

        state = request.data.get('state')
        code = request.data.get('code')

        if state == 'STATE' and code != '':
            try:
                user_ids = self.get_ding_id(code)
            except Exception:    # pylint: disable=broad-except
                return Response({'err_msg':'get dingding user time out'}, HTTP_408_REQUEST_TIMEOUT)
        else:
            return Response({'err_msg':'get tmp code error'}, HTTP_400_BAD_REQUEST)

        ding_id = user_ids['ding_id']
        ding_user = DingUser.valid_objects.filter(ding_id=ding_id).first()
        if ding_user:
            user = ding_user.user
            token = user.token
            context = {'token': token, **UserWithPermSerializer(user).data}
        else:
            context = {'token': '', 'ding_id': ding_id}
        return Response(context, HTTP_200_OK)


    def get_ding_id(self, code):
        '''
        从钉钉获取ding_id
        '''
        appid = DingConfig.get_current().qr_app_id
        appsecret = DingConfig.get_current().qr_app_secret
        access_token = requests.get(self.get_access_url, params={'appid':appid,\
            'appsecret':appsecret}).json()['access_token']
        get_psstt_code = requests.post(self.get_persistent_code_url, params={'access_token':access_token},\
        json={'tmp_auth_code':code})
        openid = get_psstt_code.json()['openid']
        persistent_code = get_psstt_code.json()['persistent_code']
        sns_token = requests.post(self.get_sns_url, params={'access_token':access_token},\
        json={'openid':openid, 'persistent_code':persistent_code}).json()['sns_token']
        user_info = requests.get(self.get_ding_info_url, params={'sns_token': sns_token}).json()['user_info']
        user_ids = {'ding_id': user_info['dingId'], 'openid': user_info['openid'], 'unionid': user_info['unionid']}
        return user_ids


class DingQueryUserAPIView(GenericAPIView):
    '''
    /ding/query/user/
    '''
    permission_classes = []
    authentication_classes = []
    @require_ding_qr_supported
    def post(self, request):
        '''
        查询用户是否注册
        '''
        sms_token = request.data.get('sms_token', '')
        if sms_token:
            mobile = SMSClaimSerializer.check_sms_token(sms_token)['mobile']
            exist = User.valid_objects.filter(mobile=mobile).exists()
            return Response({'exist': exist})
        raise ValidationError({'sms_token': ["sms_token invalid"]})


class DingBindAPIView(GenericAPIView):
    '''
    /ding/bind/
    '''
    permission_classes = []
    authentication_classes = []

    serializer_class = DingBindSerializer

    @require_ding_qr_supported
    def post(self, request):
        '''
        绑定用户
        '''
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        ding_id = serializer.validated_data['ding_id']
        ding_user = DingUser.objects.create(ding_id=ding_id, user=user)
        ding_user.save()
        token = user.token
        data = {'token':token, **UserWithPermSerializer(user).data}
        LOG_CLI(user).user_login()
        return Response(data, HTTP_201_CREATED)


class DingRegisterAndBindView(generics.CreateAPIView):
    '''
    钉钉扫码用户注册页面
    '''
    permission_classes = []
    authentication_classes = []

    serializer_class = DingRegisterAndBindSerializer
    read_serializer_class = UserWithPermSerializer


    def create(self, request, *args, **kwargs):
        '''
        钉钉扫码加绑定
        '''
        if not AccountConfig.get_current().support_ding_qr_register:
            return Response({'err_msg':'ding qr register not allowed'}, HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.save()

        cli = CLI(user)
        cli.add_users_to_group([user], Group.get_extern_root())
        data = self.read_serializer_class(user).data
        data.update(token=user.token)
        ding_id = serializer.validated_data['ding_id']
        ding_user = DingUser.objects.create(ding_id=ding_id, user=user)
        ding_user.save()
        return Response(data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        super().perform_create(serializer.instance)
        LOG_CLI(serializer.instance).user_register()
