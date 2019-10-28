'''
扫码登录视图
'''

from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED,\
    HTTP_400_BAD_REQUEST, HTTP_408_REQUEST_TIMEOUT, HTTP_403_FORBIDDEN)
from rest_framework.response import Response

from siteapi.v1.serializers.user import UserWithPermSerializer
from siteapi.v1.serializers.ucenter import (DingRegisterAndBindSerializer, DingBindSerializer, AlipayBindSerializer,
                                            AlipayRegisterAndBindSerializer)
from siteapi.v1.serializers.ucenter_work_wechat import WorkWechatRegisterAndBindSerializer, WorkWechatBindSerializer

from infrastructure.serializers.sms import SMSClaimSerializer

from executer.core import CLI
from executer.log.rdb import LOG_CLI

from oneid_meta.models import User, Group, DingUser, AlipayUser, WorkWechatUser

from oneid_meta.models.config import AlipayConfig, AccountConfig, WorkWechatConfig
from thirdparty_data_sdk.dingding.dingsdk.ding_id_manager import DingIdManager
from thirdparty_data_sdk.alipay_api import alipay_user_id_sdk
from thirdparty_data_sdk.work_wechat_sdk.user_info_manager import get_work_wechat_user_id


def require_ding_qr_supported(func):
    '''
    检查是否允许扫码登录装饰器
    '''
    def inner(self, request):
        return Response({'err_msg':'ding qr not allowed'}, HTTP_403_FORBIDDEN)\
            if not AccountConfig.get_current().support_ding_qr else func(self, request)

    return inner


def require_alipay_qr_supported(func):
    '''
    检查是否允许扫码登录装饰器
    '''
    def inner(self, request):
        return Response({'err_msg':'alipay qr not allowed'}, HTTP_403_FORBIDDEN)\
            if not AccountConfig.get_current().support_alipay_qr else func(self, request)

    return inner


def require_work_wechat_qr_supported(func):    # pylint: disable=invalid-name
    '''
    检查是否允许扫码登录
    '''
    def inner(self, request):
        return Response({'err_msg':'work wechat qr not allowed'}, HTTP_403_FORBIDDEN)\
            if not AccountConfig.get_current().support_work_wechat_qr else func(self, request)

    return inner


def check_user_exists(request):
    '''
    查询用户是否注册
    '''
    sms_token = request.data.get('sms_token', '')
    if sms_token:
        mobile = SMSClaimSerializer.check_sms_token(sms_token)['mobile']
        exist = User.valid_objects.filter(mobile=mobile).exists()
        return exist
    raise ValidationError({'sms_token': ["sms_token invalid"]})


class DingQrCallbackView(APIView):
    '''
    dingding/qr/callback/
    用戶扫码登录获取用户ding_id，openid, unionId
    '''
    permission_classes = []
    authentication_classes = []

    @require_ding_qr_supported
    def post(self, request):
        '''
        处理钉钉用户扫码之后重定向到‘首页’或‘绑定页面’
        '''

        code = request.data.get('code')

        if code != '':
            try:
                ding_id = DingIdManager(code).get_ding_id()
            except Exception:    # pylint: disable=broad-except
                return Response({'err_msg': 'get dingding user time out'}, HTTP_408_REQUEST_TIMEOUT)
        else:
            return Response({'err_msg': 'get tmp code error'}, HTTP_400_BAD_REQUEST)

        context = self.get_token(ding_id)

        return Response(context, HTTP_200_OK)

    def get_token(self, ding_id):    # pylint: disable=no-self-use
        '''
        从DingUser表查询用户，返回token
        '''
        ding_user = DingUser.valid_objects.filter(ding_id=ding_id).first()
        if ding_user:
            user = ding_user.user
            token = user.token
            context = {'token': token, **UserWithPermSerializer(user).data}
        else:
            context = {'token': '', 'user_id': ding_id}
        return context


class QrQueryUserAPIView(GenericAPIView):
    '''
    /qr/query/user/
    '''
    permission_classes = []
    authentication_classes = []

    def post(self, request):    # pylint: disable=no-self-use, missing-docstring
        return Response({'exist': check_user_exists(request)})


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
        ding_user = DingUser.objects.filter(user=user).first()
        if ding_user:
            ding_user.ding_id = ding_id
        else:
            ding_user = DingUser.objects.create(ding_id=ding_id, user=user)
        ding_user.save()
        token = user.token
        data = {'token': token, **UserWithPermSerializer(user).data}
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
            return Response({'err_msg': 'ding qr register not allowed'}, HTTP_403_FORBIDDEN)

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


class AlipayQrCallbackView(APIView):
    '''
    alipay/qr/callback/
    支付宝扫码回调视图
    '''
    permission_classes = []
    authentication_classes = []

    @require_alipay_qr_supported
    def post(self, request):
        '''
        alipay/qr/callback/
        处理支付宝用户扫码之后重定向到‘首页’或‘绑定页面’
        '''
        auth_code = request.data.get('auth_code', None)
        app_id = AlipayConfig.get_current().app_id
        if auth_code and app_id:
            alipay_user_id = self.get_alipay_user_id(auth_code, app_id)
        else:
            raise ValidationError({'auth_code and app_id': ['auth_code and app_id are required']})

        context = self.get_token(alipay_user_id)

        return Response(context, HTTP_200_OK)

    def get_token(self, alipay_user_id):    # pylint: disable=no-self-use
        '''
        从AlipayUser表查询用户，返回token
        '''
        alipay_user = AlipayUser.valid_objects.filter(alipay_user_id=alipay_user_id).first()
        if alipay_user:
            user = alipay_user.user
            token = user.token
            context = {'token': token, **UserWithPermSerializer(user).data}
        else:
            context = {'token': '', 'user_id': alipay_user_id}
        return context

    def get_alipay_user_id(self, auth_code, app_id):    # pylint: disable=no-self-use
        '''
        获取支付宝用户id
        '''
        alipay_user_id = ''
        current_app = AlipayConfig.get_current()
        if current_app:
            app_private_key = current_app.app_private_key
            alipay_public_key = current_app.alipay_public_key
            if app_private_key not in ['', None] and alipay_public_key not in ['', None]:
                try:
                    alipay_user_id = alipay_user_id_sdk.get_alipay_user_id(app_id,\
                        app_private_key, alipay_public_key, auth_code)
                except Exception as err:
                    raise ValidationError({err})
        return alipay_user_id


class AlipayBindAPIView(GenericAPIView):
    '''
    支付宝扫码绑定视图
    '''
    permission_classes = []
    authentication_classes = []

    serializer_class = AlipayBindSerializer

    @require_alipay_qr_supported
    def post(self, request):
        '''
        绑定用户
        '''
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        alipay_user_id = serializer.validated_data['alipay_user_id']
        alipay_user = AlipayUser.objects.filter(user=user).first()
        if alipay_user:
            alipay_user.alipay_user_id = alipay_user_id
        else:
            alipay_user = AlipayUser.objects.create(alipay_user_id=alipay_user_id, user=user)
        alipay_user.save()
        token = user.token
        data = {'token': token, **UserWithPermSerializer(user).data}
        LOG_CLI(user).user_login()
        return Response(data, HTTP_201_CREATED)


class AlipayRegisterAndBindView(generics.CreateAPIView):
    '''
    支付宝扫码注册加绑定视图
    '''
    permission_classes = []
    authentication_classes = []

    serializer_class = AlipayRegisterAndBindSerializer
    read_serializer_class = UserWithPermSerializer

    def create(self, request, *args, **kwargs):
        '''
        钉钉扫码加绑定
        '''
        if not AccountConfig.get_current().support_alipay_qr_register:
            return Response({'err_msg': 'alipay qr register not allowed'}, HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.save()

        cli = CLI(user)
        cli.add_users_to_group([user], Group.get_extern_root())
        data = self.read_serializer_class(user).data
        data.update(token=user.token)
        alipay_user_id = serializer.validated_data['alipay_user_id']
        alipay_user = AlipayUser.objects.create(alipay_user_id=alipay_user_id, user=user)
        alipay_user.save()
        return Response(data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        super().perform_create(serializer.instance)
        LOG_CLI(serializer.instance).user_register()


class WorkWechatQrCallbackView(APIView):
    '''
    work/wechat/qr/callback/
    企业微信用户扫码登录
    '''
    permission_classes = []
    authentication_classes = []

    @require_work_wechat_qr_supported
    def post(self, request):
        '''
        处理企业微信用户扫码之后重定向页面
        '''
        code = request.data.get('code')
        corp_id = WorkWechatConfig.get_current().corp_id
        secret = WorkWechatConfig.get_current().secret
        if code:
            work_wechat_user_id = get_work_wechat_user_id(code, corp_id, secret)
            context = self.get_token(work_wechat_user_id)
        return Response(context, HTTP_200_OK)

    def get_token(self, work_wechat_user_id):    # pylint: disable=no-self-use
        '''
        从DingUser表查询用户，返回token
        '''
        work_wechat_user = WorkWechatUser.valid_objects.filter(work_wechat_user_id=work_wechat_user_id).first()
        if work_wechat_user:
            user = work_wechat_user.user
            token = user.token
            context = {'token': token, **UserWithPermSerializer(user).data}
        else:
            context = {'token': '', 'user_id': work_wechat_user_id}
        return context


class WorkWechatBindAPIView(GenericAPIView):
    '''
    企业微信扫码绑定
    '''
    permission_classes = []
    authentication_classes = []

    serializer_class = WorkWechatBindSerializer

    @require_work_wechat_qr_supported
    def post(self, request):
        '''
        绑定用户
        '''
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        work_wechat_user_id = serializer.validated_data['work_wechat_user_id']
        work_wechat_user = WorkWechatUser.objects.filter(user=user).first()
        if work_wechat_user:
            work_wechat_user.work_wechat_user_id = work_wechat_user_id
        else:
            work_wechat_user = WorkWechatUser.objects.create(work_wechat_user_id=work_wechat_user_id, user=user)
        work_wechat_user.save()
        token = user.token
        data = {'token': token, **UserWithPermSerializer(user).data}
        LOG_CLI(user).user_login()
        return Response(data, HTTP_201_CREATED)


class WorkWechatRegisterAndBindView(generics.CreateAPIView):
    '''
    企业微信扫码注册加绑定
    '''
    permission_classes = []
    authentication_classes = []

    serializer_class = WorkWechatRegisterAndBindSerializer
    read_serializer_class = UserWithPermSerializer

    def create(self, request, *args, **kwargs):
        '''
        企业微信扫码绑定
        '''
        if not AccountConfig.get_current().support_work_wechat_qr_register:
            return Response({'err_msg': 'work wechat qr register not allowed'}, HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.save()

        cli = CLI(user)
        cli.add_users_to_group([user], Group.get_extern_root())
        data = self.read_serializer_class(user).data
        data.update(token=user.token)
        work_wechat_user_id = serializer.validated_data['work_wechat_user_id']
        work_wechat_user = WorkWechatUser.objects.create(work_wechat_user_id=work_wechat_user_id, user=user)
        work_wechat_user.save()
        return Response(data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        super().perform_create(serializer.instance)
        LOG_CLI(serializer.instance).user_register()
