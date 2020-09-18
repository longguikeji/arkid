'''
扫码登录视图
'''
# pylint: disable=too-many-lines
from urllib.parse import urlencode

from django.http import HttpResponseRedirect
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED,\
    HTTP_400_BAD_REQUEST, HTTP_408_REQUEST_TIMEOUT, HTTP_403_FORBIDDEN)
from rest_framework.response import Response

from siteapi.v1.serializers.user import UserWithPermSerializer
from siteapi.v1.serializers.ucenter import (RegisterAndBindSerializer, BindSerializer)
from infrastructure.serializers.sms import SMSClaimSerializer

from executer.core import CLI
from executer.log.rdb import LOG_CLI

from oneid_meta.models import User, Group, DingUser, AlipayUser, WechatUser, WorkWechatUser, QQUser
from oneid_meta.models.config import AlipayConfig, AccountConfig, WorkWechatConfig, WechatConfig, QQConfig

from thirdparty_data_sdk.dingding.dingsdk.ding_id_manager import DingIdManager
from thirdparty_data_sdk.alipay_api import alipay_user_id_sdk
from thirdparty_data_sdk.work_wechat_sdk.user_info_manager import WorkWechatManager
from thirdparty_data_sdk.wechat_sdk.wechat_user_info_manager import WechatUserInfoManager
from thirdparty_data_sdk.qq_sdk.qq_openid_sdk import QQInfoManager
from thirdparty_data_sdk.error_utils import APICallError


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


def require_wechat_qr_supported(func):
    '''
    检查是否允许微信扫码登录
    '''
    def inner(self, request):
        return Response({'err_msg':'wechat qr not allowed'}, HTTP_403_FORBIDDEN)\
            if not AccountConfig.get_current().support_wechat_qr else func(self, request)

    return inner


def require_work_wechat_qr_supported(func):    # pylint: disable=invalid-name
    '''
    检查是否允许企业微信扫码登录
    '''
    def inner(self, request):
        return Response({'err_msg':'work wechat qr not allowed'}, HTTP_403_FORBIDDEN)\
            if not AccountConfig.get_current().support_work_wechat_qr else func(self, request)

    return inner


def require_qq_qr_supported(func):
    '''
    检查是否允许qq扫码登录
    '''
    def inner(self, request):
        return Response({'err_msg':'qq qr not allowed'}, HTTP_403_FORBIDDEN)\
            if not AccountConfig.get_current().support_qq_qr else func(self, request)

    return inner


def check_user_exists(request):
    '''
    查询用户是否注册
    '''
    sms_token = request.data.get('sms_token', None)
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
            LOG_CLI(user).user_login()
            context = {'token': token, **UserWithPermSerializer(user).data}
        else:
            context = {'token': '', 'third_party_id': ding_id}
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

    serializer_class = BindSerializer

    @require_ding_qr_supported
    def post(self, request):
        '''
        绑定用户
        '''
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        ding_id = serializer.validated_data['user_id']
        ding_user = DingUser.valid_objects.filter(user=user).first()
        if ding_user:
            ding_user.ding_id = ding_id
        else:
            ding_user = DingUser.valid_objects.create(ding_id=ding_id, user=user)
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

    serializer_class = RegisterAndBindSerializer
    read_serializer_class = UserWithPermSerializer

    def create(self, request, *args, **kwargs):
        '''
        钉钉扫码加绑定
        '''
        if not AccountConfig.get_current().support_ding_qr_register:
            return Response({'err_msg': 'ding qr register not allowed'}, HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)

        cli = CLI(user)
        cli.add_users_to_group([user], Group.get_extern_root())
        data = self.read_serializer_class(user).data
        data.update(token=user.token)
        ding_id = serializer.validated_data['user_id']
        ding_user = DingUser.valid_objects.create(ding_id=ding_id, user=user)
        ding_user.save()
        return Response(data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        user = serializer.save()
        LOG_CLI(serializer.instance).user_register()
        return user


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
            LOG_CLI(user).user_login()
            context = {'token': token, **UserWithPermSerializer(user).data}
        else:
            context = {'token': '', 'third_party_id': alipay_user_id}
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

    serializer_class = BindSerializer

    @require_alipay_qr_supported
    def post(self, request):
        '''
        绑定用户
        '''
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        alipay_user_id = serializer.validated_data['user_id']
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

    serializer_class = RegisterAndBindSerializer
    read_serializer_class = UserWithPermSerializer

    def create(self, request, *args, **kwargs):
        '''
        钉钉扫码加绑定
        '''
        if not AccountConfig.get_current().support_alipay_qr_register:
            return Response({'err_msg': 'alipay qr register not allowed'}, HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)

        cli = CLI(user)
        cli.add_users_to_group([user], Group.get_extern_root())
        data = self.read_serializer_class(user).data
        data.update(token=user.token)
        alipay_user_id = serializer.validated_data['user_id']
        alipay_user = AlipayUser.objects.create(alipay_user_id=alipay_user_id, user=user)
        alipay_user.save()
        return Response(data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        user = serializer.save()
        LOG_CLI(serializer.instance).user_register()
        return user


class WorkWechatQrCallbackView(APIView):
    '''
    work_wechat/qr/callback/
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
            try:
                work_wechat_user_id = WorkWechatManager(corp_id=corp_id, secret=secret).get_work_wechat_user_id(code)
            except APICallError:
                raise ValidationError({'code': ['invalid']})
        else:
            raise ValidationError({'code': ['required']})
        context = self.get_token(work_wechat_user_id)
        return Response(context, HTTP_200_OK)

    def get_token(self, work_wechat_user_id):    # pylint: disable=no-self-use
        '''
        从WorkWechatUser表查询用户，返回token
        '''
        work_wechat_user = WorkWechatUser.valid_objects.filter(work_wechat_user_id=work_wechat_user_id).first()
        if work_wechat_user:
            user = work_wechat_user.user
            token = user.token
            LOG_CLI(user).user_login()
            context = {'token': token, **UserWithPermSerializer(user).data}
        else:
            context = {'token': '', 'third_party_id': work_wechat_user_id}
        return context


class WorkWechatBindAPIView(GenericAPIView):
    '''
    企业微信扫码绑定
    '''
    permission_classes = []
    authentication_classes = []

    serializer_class = BindSerializer

    @require_work_wechat_qr_supported
    def post(self, request):
        '''
        绑定用户
        '''
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        work_wechat_user_id = serializer.validated_data['user_id']
        work_wechat_user = WorkWechatUser.valid_objects.filter(user=user).first()
        if work_wechat_user:
            work_wechat_user.work_wechat_user_id = work_wechat_user_id
        else:
            work_wechat_user = WorkWechatUser.valid_objects.create(work_wechat_user_id=work_wechat_user_id, user=user)
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

    serializer_class = RegisterAndBindSerializer
    read_serializer_class = UserWithPermSerializer

    def create(self, request, *args, **kwargs):
        '''
        企业微信扫码绑定
        '''
        if not AccountConfig.get_current().support_work_wechat_qr_register:
            return Response({'err_msg': 'work wechat qr register not allowed'}, HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)

        cli = CLI(user)
        cli.add_users_to_group([user], Group.get_extern_root())
        data = self.read_serializer_class(user).data
        data.update(token=user.token)
        work_wechat_user_id = serializer.validated_data['user_id']
        work_wechat_user = WorkWechatUser.valid_objects.create(work_wechat_user_id=work_wechat_user_id, user=user)
        work_wechat_user.save()
        return Response(data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        user = serializer.save()
        LOG_CLI(serializer.instance).user_register()
        return user


class WechatQrCallbackView(APIView):
    '''
    wechat/qr/callback/
    微信用户扫码登录回调页面
    '''
    permission_classes = []
    authentication_classes = []

    @require_wechat_qr_supported
    def get(self, request):
        '''
        处理微信用户扫码之后重定向页面
        '''
        code = request.data.get('code')
        redirect_url = request.GET.get('redirect_url', None)
        appid = WechatConfig.get_current().appid
        secret = WechatConfig.get_current().secret
        if code:
            try:
                unionid = WechatUserInfoManager(appid=appid, secret=secret).get_union_id(code)
            except APICallError:
                raise ValidationError({'code': ['invalid']})
        else:
            raise ValidationError({'code': ['required']})

        context = self.get_token(unionid)
        if redirect_url:
            query_string = urlencode(context)
            return HttpResponseRedirect(f'{redirect_url}?{query_string}')
        return Response(context, HTTP_200_OK)

    def get_token(self, unionid):    # pylint: disable=no-self-use
        '''
        从Wechat表查询用户，返回token
        '''
        wechat_user = WechatUser.valid_objects.filter(unionid=unionid).first()
        if wechat_user:
            user = wechat_user.user
            token = user.token
            LOG_CLI(user).user_login()
            context = {'token': token, **UserWithPermSerializer(user).data}
        else:
            context = {'token': '', 'third_party_id': unionid}
        return context


class WechatBindAPIView(GenericAPIView):
    '''
    微信扫码绑定
    '''
    permission_classes = []
    authentication_classes = []

    serializer_class = BindSerializer

    @require_wechat_qr_supported
    def post(self, request):
        '''
        绑定用户
        '''
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        unionid = serializer.validated_data['user_id']
        wechat_user = WechatUser.valid_objects.filter(user=user).first()
        if wechat_user:
            wechat_user.unionid = unionid
        else:
            wechat_user = WechatUser.valid_objects.create(unionid=unionid, user=user)
        wechat_user.save()
        token = user.token
        data = {'token': token, **UserWithPermSerializer(user).data}
        LOG_CLI(user).user_login()
        return Response(data, HTTP_201_CREATED)


class WechatRegisterAndBindView(generics.CreateAPIView):
    '''
    微信扫码注册加绑定
    '''
    permission_classes = []
    authentication_classes = []

    serializer_class = RegisterAndBindSerializer
    read_serializer_class = UserWithPermSerializer

    def create(self, request, *args, **kwargs):
        '''
        微信扫码注册并绑定
        '''
        if not AccountConfig.get_current().support_wechat_qr_register:
            return Response({'err_msg': 'wechat qr register not allowed'}, HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)

        cli = CLI(user)
        cli.add_users_to_group([user], Group.get_extern_root())
        data = self.read_serializer_class(user).data
        data.update(token=user.token)
        unionid = serializer.validated_data['user_id']
        wechat_user = WechatUser.valid_objects.create(unionid=unionid, user=user)
        wechat_user.save()
        return Response(data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        user = serializer.save()
        LOG_CLI(serializer.instance).user_register()
        return user


class QQQrCallbackView(APIView):
    '''
    qq/qr/callback/
    '''
    permission_classes = []
    authentication_classes = []

    @require_qq_qr_supported
    def post(self, request):
        '''
        处理qq用户扫码之后重定向到‘首页’或‘绑定页面’
        '''
        code = request.data.get('code')

        try:
            app_id = QQConfig.get_current().app_id
            app_key = QQConfig.get_current().app_key
            open_id = QQInfoManager(app_id, app_key).get_open_id(code)
        except APICallError:    # pylint: disable=broad-except
            return Response({'code': 'invalid'}, HTTP_400_BAD_REQUEST)

        context = self.get_token(open_id)

        return Response(context, HTTP_200_OK)

    def get_token(self, open_id):    # pylint: disable=no-self-use
        '''
        从QQUser表查询用户，返回token
        '''
        qq_user = QQUser.valid_objects.filter(open_id=open_id).first()
        if qq_user:
            user = qq_user.user
            token = user.token
            LOG_CLI(user).user_login()
            context = {'token': token, **UserWithPermSerializer(user).data}
        else:
            context = {'token': '', 'third_party_id': open_id}
        return context


class QQBindAPIView(GenericAPIView):
    '''
    /ding/bind/
    '''
    permission_classes = []
    authentication_classes = []

    serializer_class = BindSerializer

    @require_qq_qr_supported
    def post(self, request):
        '''
        绑定用户
        '''
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        open_id = serializer.validated_data['user_id']
        qq_user = QQUser.valid_objects.filter(user=user).first()
        if qq_user:
            qq_user.open_id = open_id
        else:
            qq_user = QQUser.valid_objects.create(open_id=open_id, user=user)
        qq_user.save()
        token = user.token
        data = {'token': token, **UserWithPermSerializer(user).data}
        LOG_CLI(user).user_login()
        return Response(data, HTTP_201_CREATED)


class QQRegisterAndBindView(generics.CreateAPIView):
    '''
    qq扫码用户注册页面
    '''
    permission_classes = []
    authentication_classes = []

    serializer_class = RegisterAndBindSerializer
    read_serializer_class = UserWithPermSerializer

    def create(self, request, *args, **kwargs):
        '''
        qq扫码加绑定
        '''
        if not AccountConfig.get_current().support_qq_qr_register:
            return Response({'err_msg': 'qq qr register not allowed'}, HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)

        cli = CLI(user)
        cli.add_users_to_group([user], Group.get_extern_root())
        data = self.read_serializer_class(user).data
        data.update(token=user.token)
        open_id = serializer.validated_data['user_id']
        qq_user = QQUser.valid_objects.create(open_id=open_id, user=user)
        qq_user.save()
        return Response(data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        user = serializer.save()
        LOG_CLI(serializer.instance).user_register()
        return user
