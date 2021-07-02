import os
from rest_framework.views import APIView
from django.http import HttpResponseRedirect
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from .user_info_manager import ArkIDUserInfoManager, APICallError
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from .models import ArkIDUser
from urllib.parse import urlencode, unquote
import urllib.parse
from django.urls import reverse
from config import get_app_config
from tenant.models import Tenant
from drf_spectacular.utils import extend_schema
from .provider import ArkIDExternalIdpProvider
from .serializers import ArkIDBindSerializer

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


@extend_schema(tags=["arkid"])
class ArkIDLoginView(APIView):

    permission_classes = []
    authentication_classes = []

    def get(self, request, tenant_uuid):
        c = get_app_config()
        # @TODO: keep other query params

        provider = ArkIDExternalIdpProvider()
        provider.load_data(tenant_uuid=tenant_uuid)

        next_url = request.GET.get("next", None)
        if next_url is not None:
            next_url = "?next=" + urllib.parse.quote(next_url)
        else:
            next_url = ""

        redirect_uri = "{}{}".format(provider.callback_url, next_url)
        url = "{}?client_id={}&redirect_uri={}&response_type=code&scope=userinfo".format(
            provider.authorize_url,
            provider.client_id,
            urllib.parse.quote(redirect_uri),
        )
        return HttpResponseRedirect(url)


@extend_schema(tags=["arkid"])
class ArkIDBindAPIView(GenericAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = ArkIDBindSerializer

    def post(self, request, tenant_uuid):
        """
        绑定用户
        """
        tenant = Tenant.objects.filter(uuid=tenant_uuid).first()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        arkid_user_id = serializer.validated_data['user_id']
        arkid_user = ArkIDUser.valid_objects.filter(user=user, tenant=tenant).first()
        if arkid_user:
            arkid_user.arkid_user_id = arkid_user_id
        else:
            arkid_user = ArkIDUser.valid_objects.create(arkid_user_id=arkid_user_id, user=user, tenant=tenant)
        arkid_user.save()
        token = user.token
        data = {"token": token}
        return Response(data, HTTP_200_OK)


@extend_schema(tags=["arkid"])
class ArkIDCallbackView(APIView):

    permission_classes = []
    authentication_classes = []

    def get(self, request, tenant_uuid):
        """
        处理arkid用户登录之后重定向页面
        """
        code = request.GET["code"]
        token = request.GET["token"]
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
                provider = ArkIDExternalIdpProvider()
                provider.load_data(tenant_uuid=tenant_uuid)
                user_id = ArkIDUserInfoManager(
                    provider.client_id,
                    provider.secret_id,
                    "{}{}".format(
                        provider.callback_url,
                        next_url,
                    ),
                    tenant_uuid,
                ).get_user_id(code)
            except APICallError as error:
                raise ValidationError({"code": ["invalid"], "message": error})
        else:
            raise ValidationError({"code": ["required"]})

        context = self.get_token(user_id, tenant_uuid, token)
        if next_url:
            next_url = next_url.replace("?next=", "")
            query_string = urlencode(context)
            url = f"{next_url}?{query_string}"
            url = unquote(url)
            return HttpResponseRedirect(url)

        return Response(context, HTTP_200_OK)

    def get_token(self, user_id, tenant_uuid, default_token):  # pylint: disable=no-self-use
        arkid_user = ArkIDUser.valid_objects.filter(arkid_user_id=user_id).first()
        if arkid_user:
            user = arkid_user.user
            token = user.token
            context = {"token": token, "tenant_uuid": tenant_uuid}
        else:
            tenant = Tenant.objects.filter(uuid=tenant_uuid).first()
            key_obj = Token.objects.filter(key=default_token).first()
            user = key_obj.user
            arkid_user = ArkIDUser.valid_objects.create(arkid_user_id=user_id, user=user, tenant=tenant)
            context = {"token": user.token, "tenant_uuid": tenant_uuid}
        return context


@extend_schema(tags=["arkid"])
class ArkIDUnBindView(GenericAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    def get(self, request, tenant_uuid):
        """
        解除绑定用户
        """
        tenant = Tenant.objects.filter(uuid=tenant_uuid).first()
        arkid_user = ArkIDUser.valid_objects.filter(user=request.user, tenant=tenant).first()
        if arkid_user:
            arkid_user.kill()
            data = {"is_del": True}
        else:
            data = {"is_del": False}
        return Response(data, HTTP_200_OK)
