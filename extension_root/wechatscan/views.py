import os
import requests
from rest_framework.views import APIView
from django.http import HttpResponseRedirect
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from .user_info_manager import WeChatScanUserInfoManager, APICallError
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from .models import WeChatScanUser, WeChatScanInfo
from urllib.parse import urlencode, unquote
import urllib.parse
from django.urls import reverse
from config import get_app_config
from tenant.models import Tenant
from .constants import AUTHORIZE_URL, FRESH_TOKEN_URL
from drf_spectacular.utils import extend_schema
from .provider import WeChatScanExternalIdpProvider
from .serializers import WeChatScanBindSerializer

import uuid

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


@extend_schema(tags=["wechatscan"])
class WeChatScanLoginView(APIView):

    permission_classes = []
    authentication_classes = []

    def get(self, request, tenant_uuid):
        c = get_app_config()
        # @TODO: keep other query params

        provider = WeChatScanExternalIdpProvider()
        provider.load_data(tenant_uuid=tenant_uuid)
        host = c.get_host()
        callback_url = host+reverse("api:wechatscan:callback", args=[tenant_uuid])

        next_url = request.GET.get("next", None)
        if next_url is not None:
            next_url = urllib.parse.quote("?next=" + urllib.parse.quote(next_url))
        else:
            next_url = ""
        # return_url = request.GET.get("return_url", None)
        # if not return_url:
        #     raise ValidationError({"return_url": ["required"]})

        url = "{}?appid={}&redirect_uri={}&response_type=code&scope=snsapi_login&state={}".format(
            AUTHORIZE_URL,
            provider.appid,
            callback_url+next_url,
            uuid.uuid1().hex,
        )
        return HttpResponseRedirect(url)


@extend_schema(tags=["wechatscan"])
class WeChatScanCallbackView(APIView):

    permission_classes = []
    authentication_classes = []

    def get(self, request, tenant_uuid):
        """
        处理wechatscan用户登录之后重定向页面
        """

        code = request.GET.get("code")

        next_url = request.GET.get("next", None)
        frontend_host = get_app_config().get_frontend_host().replace('http://' , '').replace('https://' , '')
        if "third_part_callback" not in next_url or frontend_host not in next_url:
            return Response({'error_msg': '错误的跳转页面'}, HTTP_200_OK)
        if next_url is not None:
            next_url = "?next=" + urllib.parse.quote(next_url)
        else:
            next_url = ""
        
        if code:
            try:
                provider = WeChatScanExternalIdpProvider()
                provider.load_data(tenant_uuid=tenant_uuid)
                openid, unionid, nickname, avatar, access_token, refresh_token = WeChatScanUserInfoManager(
                    provider.appid,
                    provider.secret,
                ).get_user_info(code)
            except APICallError as error:
                raise ValidationError({"code": ["invalid"], "message": error})
        else:
            raise ValidationError({"code": ["required"]})

        context = self.get_token(openid, unionid, nickname, avatar, access_token, refresh_token, tenant_uuid)
        if next_url:
            next_url = next_url.replace("?next=", "")
            print("****************")
            query_string =urllib.parse.urlencode(context)
            url = f"{next_url}?{query_string}"
            url = urllib.parse.unquote(url)
            return HttpResponseRedirect(url)

        return Response(context, HTTP_200_OK)

    def get_token(self, openid, unionid, nickname, avatar, access_token, refresh_token, tenant_uuid):  # pylint: disable=no-self-use
        wechatscan_user = WeChatScanUser.valid_objects.filter(openid=openid).first()
        # 用户信息
        wechatscaninfo, created = WeChatScanInfo.objects.get_or_create(
            is_del=False,
            openid=openid,
        )
        wechatscaninfo.access_token = access_token
        wechatscaninfo.refresh_token = refresh_token
        wechatscaninfo.unionid = unionid
        wechatscaninfo.nickname = nickname
        wechatscaninfo.avatar = avatar
        wechatscaninfo.save()
        if wechatscan_user:
            user = wechatscan_user.user
            token = user.token
            context = {"token": token}
        else:
            context = {
                "token": "",
                "user_id": openid,
                "bind": reverse(
                    "api:wechatscan:bind",
                    args=[
                        tenant_uuid,
                    ],
                ),
            }
        return context


@extend_schema(tags=["wechatscan"])
class WeChatScanBindAPIView(GenericAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]
    serializer_class = WeChatScanBindSerializer

    def post(self, request, tenant_uuid):
        """
        绑定用户
        """
        tenant = Tenant.objects.filter(uuid=tenant_uuid).first()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        openid = serializer.validated_data['user_id']
        wechatscan_user = WeChatScanUser.valid_objects.filter(user=user, tenant=tenant).first()
        if wechatscan_user:
            wechatscan_user.openid = openid
        else:
            wechatscan_user = WeChatScanUser.valid_objects.create(openid=openid, user=user, tenant=tenant)
        wechatscan_user.save()
        token = user.token
        data = {"token": token}
        return Response(data, HTTP_200_OK)


@extend_schema(tags=["wechatscan"])
class WeChatScanUnBindView(GenericAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    def get(self, request, tenant_uuid):
        """
        解除绑定用户
        """
        tenant = Tenant.objects.filter(uuid=tenant_uuid).first()
        wechatscan_user = WeChatScanUser.valid_objects.filter(user=request.user, tenant=tenant).first()
        if wechatscan_user:
            wechatscan_user.kill()
            data = {"is_del": True}
        else:
            data = {"is_del": False}
        return Response(data, HTTP_200_OK)


@extend_schema(tags=["wechatscan"])
class WeChatScanUserInfoAPIView(GenericAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    def get(self, request, tenant_uuid):
        """
        用户信息
        """
        tenant = Tenant.objects.filter(uuid=tenant_uuid).first()
        wechatscan_user = WeChatScanUser.valid_objects.filter(user=request.user, tenant=tenant).first()
        if not wechatscan_user:
            return Response({'error_msg': '需要先绑定后才能获取用户信息'}, HTTP_200_OK)
        info = WeChatScanInfo.valid_objects.filter(
            openid=wechatscan_user.openid
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
