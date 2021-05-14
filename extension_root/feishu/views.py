from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from config import get_app_config
from .provider import FeishuExternalIdpProvider
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from .user_info_manager import FeishuUserInfoManager, APICallError
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from django.http import HttpResponseRedirect
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from .serializers import FeishuBindSerializer
from .constants import AUTHORIZE_URL
from .models import FeishuUser
from tenant.models import Tenant
from django.urls import reverse
import urllib.parse


@extend_schema(tags=["feishu"])
class FeishuLoginView(APIView):

    permission_classes = []
    authentication_classes = []

    def get(self, request, tenant_uuid):
        c = get_app_config()
        # @TODO: keep other query params

        provider = FeishuExternalIdpProvider()
        provider.load_data(tenant_uuid=tenant_uuid)

        next_url = request.GET.get("next", None)
        if next_url is not None:
            next_url = "?next=" + urllib.parse.quote(next_url)
        else:
            next_url = ""
        redirect_uri = urllib.parse.quote("{}{}{}".format(c.get_host(), reverse(
            "api:feishu:callback",
            args=[
                tenant_uuid,
            ],
        ), next_url))
        url = "{}?app_id={}&redirect_uri={}".format(
            AUTHORIZE_URL,
            provider.app_id,
            redirect_uri,
        )
        return HttpResponseRedirect(url)


@extend_schema(tags=["feishu"])
class FeishuCallbackView(APIView):

    permission_classes = []
    authentication_classes = []

    def get(self, request, tenant_uuid):
        '''
        处理feishu用户登录之后重定向页面
        '''
        code = request.GET["code"]
        next_url = request.GET.get("next", None)
        if next_url is not None:
            next_url = "?next=" + urllib.parse.quote(next_url)
        else:
            next_url = ""
        if code:
            try:
                provider = FeishuExternalIdpProvider()
                provider.load_data(tenant_uuid=tenant_uuid)

                user_id = FeishuUserInfoManager(provider.app_id, provider.secret_id, provider._get_token()).get_user_id(code, next_url)
            except APICallError:
                raise ValidationError({"code": ["invalid"]})
        else:
            raise ValidationError({"code": ["required"]})

        context = self.get_token(user_id, tenant_uuid)
        if next_url:
            next_url = next_url.replace("?next=", "")
            print("****************")
            query_string = urlencode(context)
            url = f"{next_url}?{query_string}"
            url = unquote(url)
            return HttpResponseRedirect(url)

        return Response(context, HTTP_200_OK)

    def get_token(self, user_id, tenant_uuid):  # pylint: disable=no-self-use
        feishu_user = FeishuUser.valid_objects.filter(feishu_user_id=user_id).first()
        if feishu_user:
            user = feishu_user.user
            token = user.token
            # context = {"token": token, **UserWithPermSerializer(user).data}
            context = {"token": token}
        else:
            # context = {"token": "", "feishu_user_id": user_id}
            context = {
                "token": "",
                "user_id": user_id,
                "bind": reverse(
                    "api:feishu:bind",
                    args=[
                        tenant_uuid,
                    ],
                ),
            }

        return context


@extend_schema(tags=["feishu"])
class FeishuBindView(GenericAPIView):

    permission_classes = [AllowAny]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = FeishuBindSerializer

    def post(self, request, tenant_uuid):
        """
        绑定用户
        """
        tenant = Tenant.objects.filter(uuid=tenant_uuid).first()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        feishu_user_id = serializer.validated_data['user_id']
        feishu_user = FeishuUser.valid_objects.filter(user=user, tenant=tenant).first()
        if feishu_user:
            feishu_user.feishu_user_id = feishu_user_id
        else:
            feishu_user = FeishuUser.valid_objects.create(feishu_user_id=feishu_user_id, user=user, tenant=tenant)
        feishu_user.save()
        token = user.token
        data = {"token": token}
        return Response(data, HTTP_200_OK)


@extend_schema(tags=["feishu"])
class FeishuUnBindView(GenericAPIView):

    permission_classes = [AllowAny]
    authentication_classes = [ExpiringTokenAuthentication]

    def get(self, request, tenant_uuid):
        """
        解除绑定用户
        """
        tenant = Tenant.objects.filter(uuid=tenant_uuid).first()
        feishuuser = FeishuUser.valid_objects.filter(user=request.user, tenant=tenant).first()
        if feishuuser:
            feishuuser.kill()
            data = {"is_del": True}
        else:
            data = {"is_del": False}
        return Response(data, HTTP_200_OK)
