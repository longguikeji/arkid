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
from .constants import AUTHORIZE_URL
from drf_spectacular.utils import extend_schema
from .provider import WeChatWorkExternalIdpProvider
from .serializers import WeChatWorkBindSerializer

import uuid

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
        # callback_url = callback_url.replace("localhost:8000", "loopbing.natapp1.cc")

        next_url = request.GET.get("next", None)
        if next_url is not None:
            next_url = urllib.parse.quote("?next=" + urllib.parse.quote(next_url))
        else:
            next_url = ""

        callback_url = callback_url+next_url
        url = AUTHORIZE_URL.format(provider.corpid,callback_url,uuid.uuid1().hex)
        return HttpResponseRedirect(url)


@extend_schema(tags=["wechatwork"])
class WeChatWorkCallbackView(APIView):

    permission_classes = []
    authentication_classes = []

    def get(self, request, tenant_uuid):
        """
        处理wechatwork用户登录之后重定向页面
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
                provider = WeChatWorkExternalIdpProvider()
                provider.load_data(tenant_uuid=tenant_uuid)
                access_token, device_id, work_user_id = WeChatWorkUserInfoManager(
                    provider.corpid,
                    provider.corpsecret,
                ).get_user_info(code)
            except APICallError as error:
                raise ValidationError({"code": ["invalid"], "message": error})
        else:
            raise ValidationError({"code": ["required"]})

        context = self.get_token(access_token, device_id, work_user_id, tenant_uuid)
        if next_url:
            next_url = next_url.replace("?next=", "")
            print("****************")
            query_string =urllib.parse.urlencode(context)
            url = f"{next_url}?{query_string}"
            url = urllib.parse.unquote(url)
            return HttpResponseRedirect(url)

        return Response(context, HTTP_200_OK)

    def get_token(self, access_token, device_id, user_id, tenant_uuid):  # pylint: disable=no-self-use
        wechatwork_user = WeChatWorkUser.valid_objects.filter(work_user_id=user_id).first()
        # 用户信息
        wechatworkinfo, created = WeChatWorkInfo.objects.get_or_create(
            is_del=False,
            work_user_id=user_id,
        )
        wechatworkinfo.access_token = access_token
        wechatworkinfo.device_id = device_id
        wechatworkinfo.save()

        if wechatwork_user:
            user = wechatwork_user.user
            token = user.token
            context = {"token": token}
        else:
            context = {
                "token": "",
                "user_id": user_id,
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
        user_id = serializer.validated_data['user_id']
        wechatwork_user = WeChatWorkUser.valid_objects.filter(user=user, tenant=tenant).first()
        if wechatwork_user:
            wechatwork_user.work_user_id = user_id
        else:
            wechatwork_user = WeChatWorkUser.valid_objects.create(work_user_id=user_id, user=user, tenant=tenant)
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
            work_user_id=wechatwork_user.work_user_id
        ).first()
        data = {
            "user_id": info.work_user_id,
            "access_token": info.access_token,
            "device_id": info.device_id,
        }
        return Response(data, HTTP_200_OK)
