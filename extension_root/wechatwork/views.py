import os
import requests
from rest_framework.views import APIView
from django.http import HttpResponseRedirect
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from .user_info_manager import WeChatWorkUserInfoManager, APICallError
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from .models import WeChatWorkUser, WeChatWorkInfo
from urllib.parse import urlencode, unquote
import urllib.parse
from django.urls import reverse
from config import get_app_config
from tenant.models import Tenant
from .constants import AUTHORIZE_URL, FRESH_TOKEN_URL
from drf_spectacular.utils import extend_schema
from .provider import WeChatWorkExternalIdpProvider
from .serializers import WeChatWorkBindSerializer

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


@extend_schema(tags=["wechatwork"])
class WeChatWorkLoginView(APIView):

    permission_classes = []
    authentication_classes = []

    def get(self, request, tenant_uuid):
        c = get_app_config()
        # @TODO: keep other query params

        provider = WeChatWorkExternalIdpProvider()
        provider.load_data(tenant_uuid=tenant_uuid)
        host = c.get_host()
        callback_url = host+reverse("api:wechatwork:callback", args=[tenant_uuid])
        callback_url = callback_url.replace("localhost:8000","loopbing.natapp1.cc")
        return_url = request.GET.get("return_url", None)
        if not return_url:
            raise ValidationError({"return_url": ["required"]})
        url = "{}?appid={}&redirect_uri={}&response_type=code&scope=snsapi_login&state={}".format(
            AUTHORIZE_URL,
            provider.appid,
            callback_url,
            return_url,
        )
        return HttpResponseRedirect(url)


@extend_schema(tags=["wechatwork"])
class WeChatWorkCallbackView(APIView):

    permission_classes = []
    authentication_classes = []

    def get(self, request, tenant_uuid):
        """
        处理wechatwork用户登录之后重定向页面
        """
        code = request.GET["code"]
        return_url = request.GET.get("state", None)
        if code:
            try:
                provider = WeChatWorkExternalIdpProvider()
                provider.load_data(tenant_uuid=tenant_uuid)
                openid, unionid, nickname, avatar, access_token, refresh_token = WeChatWorkUserInfoManager(
                    provider.appid,
                    provider.secret,
                ).get_user_info(code)
            except APICallError as error:
                raise ValidationError({"code": ["invalid"], "message": error})
        else:
            raise ValidationError({"code": ["required"]})

        context = self.get_token(openid, unionid, nickname, avatar, access_token, refresh_token, tenant_uuid)
        if return_url:
            query_string = urlencode(context)
            url = f"{return_url}?{query_string}"
            url = unquote(url)
            return HttpResponseRedirect(url)

        return Response(context, HTTP_200_OK)

    def get_token(self, openid, unionid, nickname, avatar, access_token, refresh_token, tenant_uuid):  # pylint: disable=no-self-use
        wechatwork_user = WeChatWorkUser.valid_objects.filter(openid=openid).first()
        # 用户信息
        wechatworkinfo, created = WeChatWorkInfo.objects.get_or_create(
            is_del=False,
            openid=openid,
        )
        wechatworkinfo.access_token = access_token
        wechatworkinfo.refresh_token = refresh_token
        wechatworkinfo.unionid = unionid
        wechatworkinfo.nickname = nickname
        wechatworkinfo.avatar = avatar
        wechatworkinfo.save()
        if wechatwork_user:
            user = wechatwork_user.user
            token = user.token
            context = {"token": token}
        else:
            context = {
                "token": "",
                "openid": openid,
                "bind": reverse(
                    "api:wechatwork:bind",
                    args=[
                        tenant_uuid,
                    ],
                ),
            }
        return context


@extend_schema(tags=["wechatwork"])
class WeChatWorkBindAPIView(GenericAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]
    serializer_class = WeChatWorkBindSerializer

    def post(self, request, tenant_uuid):
        """
        绑定用户
        """
        tenant = Tenant.objects.filter(uuid=tenant_uuid).first()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        openid = serializer.validated_data['openid']
        wechatwork_user = WeChatWorkUser.valid_objects.filter(user=user, tenant=tenant).first()
        if wechatwork_user:
            wechatwork_user.openid = openid
        else:
            wechatwork_user = WeChatWorkUser.valid_objects.create(openid=openid, user=user, tenant=tenant)
        wechatwork_user.save()
        token = user.token
        data = {"token": token}
        return Response(data, HTTP_200_OK)


@extend_schema(tags=["wechatwork"])
class WeChatWorkUnBindView(GenericAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    def get(self, request, tenant_uuid):
        """
        解除绑定用户
        """
        tenant = Tenant.objects.filter(uuid=tenant_uuid).first()
        wechatwork_user = WeChatWorkUser.valid_objects.filter(user=request.user, tenant=tenant).first()
        if wechatwork_user:
            wechatwork_user.kill()
            data = {"is_del": True}
        else:
            data = {"is_del": False}
        return Response(data, HTTP_200_OK)


@extend_schema(tags=["wechatwork"])
class WeChatWorkUserInfoAPIView(GenericAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    def get(self, request, tenant_uuid):
        """
        用户信息
        """
        tenant = Tenant.objects.filter(uuid=tenant_uuid).first()
        wechatwork_user = WeChatWorkUser.valid_objects.filter(user=request.user, tenant=tenant).first()
        if not wechatwork_user:
            return Response({'error_msg': '需要先绑定后才能获取用户信息'}, HTTP_200_OK)
        info = WeChatWorkInfo.valid_objects.filter(
            openid=wechatwork_user.openid
        ).first()
        data = {
            "openid": info.openid,
            "access_token": info.access_token,
            "refresh_token": info.refresh_token,
            "unionid": info.unionid,
            "nickname": info.nickname,
            "avatar": info.avatar,
        }
        return Response(data, HTTP_200_OK)
