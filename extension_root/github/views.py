import os
from rest_framework.views import APIView
from django.http import HttpResponseRedirect
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_403_FORBIDDEN, HTTP_201_CREATED, HTTP_200_OK
from rest_framework.views import APIView
from .user_info_manager import GithubUserInfoManager, APICallError
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from .models import GithubUser
from urllib.parse import urlencode, unquote
import urllib.parse
from django.urls import reverse
from config import get_app_config
from tenant.models import Tenant
from .constants import AUTHORIZE_URL
from drf_spectacular.utils import extend_schema
from .provider import GithubExternalIdpProvider
from .serializers import GithubBindSerializer

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


@extend_schema(tags=["github"])
class GithubLoginView(APIView):

    permission_classes = []
    authentication_classes = []

    def get(self, request, tenant_uuid):
        c = get_app_config()
        # @TODO: keep other query params
        provider = GithubExternalIdpProvider()
        provider.load_data(tenant_uuid=tenant_uuid)
        next_url = request.GET.get("next", None)
        if next_url is not None:
            next_url = "?next=" + next_url
        else:
            next_url = ""
        redirect_uri = "{}{}{}".format(c.get_host(), provider.callback_url, next_url)
        url = "{}?client_id={}&redirect_uri={}".format(
            AUTHORIZE_URL,
            provider.client_id,
            redirect_uri,
        )

        return HttpResponseRedirect(url)


@extend_schema(tags=["github"])
class GithubBindAPIView(GenericAPIView):
    """
    Github账号绑定
    """

    permission_classes = [AllowAny]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = GithubBindSerializer

    def post(self, request, tenant_uuid):
        """
        绑定用户
        """
        tenant = Tenant.objects.filter(uuid=tenant_uuid).first()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        github_user_id = serializer.validated_data['user_id']
        github_user = GithubUser.valid_objects.filter(user=user, tenant=tenant).first()
        if github_user:
            github_user.github_user_id = github_user_id
        else:
            github_user = GithubUser.valid_objects.create(
                github_user_id=github_user_id, user=user, tenant=tenant
            )
        github_user.save()
        token = user.token
        data = {"token": token}
        return Response(data, HTTP_200_OK)


@extend_schema(tags=["github"])
class GithubCallbackView(APIView):

    permission_classes = []
    authentication_classes = []

    def get(self, request, tenant_uuid):
        """
        处理github用户登录之后重定向页面
        """
        code = request.GET["code"]
        next_url = request.GET.get("next", None)
        if code:
            try:
                provider = GithubExternalIdpProvider()
                provider.load_data(tenant_uuid=tenant_uuid)
                user_id = GithubUserInfoManager(
                    provider.client_id, provider.secret_id
                ).get_user_id(code)
            except APICallError:
                raise ValidationError({"code": ["invalid"]})
        else:
            raise ValidationError({"code": ["required"]})

        context = self.get_token(user_id, tenant_uuid)
        if next_url:
            query_string = urlencode(context)
            url = f"{next_url}?{query_string}"
            url = unquote(url)
            return HttpResponseRedirect(url)
        return Response(context, HTTP_200_OK)

    def get_token(self, user_id, tenant_uuid):  # pylint: disable=no-self-use
        github_user = GithubUser.valid_objects.filter(github_user_id=user_id).first()
        if github_user:
            user = github_user.user
            token = user.token
            context = {"token": token}
        else:
            context = {
                "token": "",
                "user_id": user_id,
                "tenant_uuid": tenant_uuid,
                "bind": reverse(
                    "api:github:bind",
                    args=[
                        tenant_uuid,
                    ],
                ),
            }

        return context


@extend_schema(tags=["github"])
class GithubUnBindView(GenericAPIView):

    permission_classes = [AllowAny]
    authentication_classes = [ExpiringTokenAuthentication]

    def get(self, request, tenant_uuid):
        """
        解除绑定用户
        """
        tenant = Tenant.objects.filter(uuid=tenant_uuid).first()
        github_user = GithubUser.valid_objects.filter(user=request.user, tenant=tenant).first()
        if github_user:
            github_user.delete()
            data = {"is_del": True}
        else:
            data = {"is_del": False}
        return Response(data, HTTP_200_OK)


@extend_schema(tags=["github"])
class GithubRegisterAndBindView(generics.CreateAPIView):
    """
    github账户注册加绑定
    """

    permission_classes = []
    authentication_classes = []

    # serializer_class = RegisterAndBindSerializer
    # read_serializer_class = UserWithPermSerializer

    # def create(self, request, *args, **kwargs):
    #     """
    #     github账户注册并绑定
    #     """

    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     user = self.perform_create(serializer)

    #     cli = CLI(user)
    #     cli.add_users_to_group([user], Group.get_extern_root())
    #     data = self.read_serializer_class(user).data
    #     data.update(token=user.token)
    #     user_id = serializer.validated_data['user_id']
    #     github_user = GithubUser.valid_objects.create(github_user_id=user_id, user=user)
    #     github_user.save()
    #     return Response(data, status=status.HTTP_201_CREATED)

    # def perform_create(self, serializer):
    #     user = serializer.save()
    #     LOG_CLI(serializer.instance).user_register()
    #     return user
