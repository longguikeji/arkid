import os
from rest_framework.views import APIView
from django.http import HttpResponseRedirect
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from .user_info_manager import GiteeUserInfoManager, APICallError
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from .models import GiteeUser
from urllib.parse import urlencode, unquote
import urllib.parse
from django.urls import reverse
from config import get_app_config
from tenant.models import Tenant
from .constants import AUTHORIZE_URL
from drf_spectacular.utils import extend_schema
from .provider import GiteeExternalIdpProvider
from .serializers import GiteeBindSerializer

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


@extend_schema(tags=["gitee"])
class GiteeLoginView(APIView):

    permission_classes = []
    authentication_classes = []

    def get(self, request, tenant_uuid):
        c = get_app_config()
        # @TODO: keep other query params

        provider = GiteeExternalIdpProvider()
        provider.load_data(tenant_uuid=tenant_uuid)

        next_url = request.GET.get("next", None)
        if next_url is not None:
            next_url = "?next=" + urllib.parse.quote(next_url)
        else:
            next_url = ""

        redirect_uri = "{}{}{}".format(c.get_host(), provider.callback_url, next_url)

        url = "{}?client_id={}&redirect_uri={}&response_type=code&scope=user_info".format(
            AUTHORIZE_URL,
            provider.client_id,
            urllib.parse.quote(redirect_uri),
        )

        return HttpResponseRedirect(url)


@extend_schema(tags=["gitee"])
class GiteeBindAPIView(GenericAPIView):

    permission_classes = [AllowAny]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = GiteeBindSerializer

    def post(self, request, tenant_uuid):
        """
        绑定用户
        """
        tenant = Tenant.objects.filter(uuid=tenant_uuid).first()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        gitee_user_id = serializer.validated_data['user_id']
        github_user = GiteeUser.valid_objects.filter(user=user, tenant=tenant).first()
        if github_user:
            github_user.gitee_user_id = gitee_user_id
        else:
            github_user = GiteeUser.valid_objects.create(gitee_user_id=gitee_user_id, user=user, tenant=tenant)
        github_user.save()
        token = user.token
        data = {"token": token}
        return Response(data, HTTP_200_OK)


@extend_schema(tags=["gitee"])
class GiteeCallbackView(APIView):

    permission_classes = []
    authentication_classes = []

    def get(self, request, tenant_uuid):
        """
        处理gitee用户登录之后重定向页面
        """
        code = request.GET["code"]
        next_url = request.GET.get("next", None)
        if next_url is not None:
            next_url = "?next=" + urllib.parse.quote(next_url)
        else:
            next_url = ""
        if code:
            try:
                provider = GiteeExternalIdpProvider()
                provider.load_data(tenant_uuid=tenant_uuid)
                user_id = GiteeUserInfoManager(
                    provider.client_id,
                    provider.secret_id,
                    "{}{}{}".format(
                        get_app_config().get_host(),
                        provider.callback_url,
                        next_url,
                    )
                ).get_user_id(code)
            except APICallError as error:
                raise ValidationError({"code": ["invalid"], "message": error})
        else:
            raise ValidationError({"code": ["required"]})

        context = self.get_token(user_id, tenant_uuid)
        if next_url:
            next_url = next_url.replace("?next=", "")
            query_string = urlencode(context)
            url = f"{next_url}?{query_string}"
            url = unquote(url)
            return HttpResponseRedirect(url)

        return Response(context, HTTP_200_OK)

    def get_token(self, user_id, tenant_uuid):  # pylint: disable=no-self-use
        gitee_user = GiteeUser.valid_objects.filter(gitee_user_id=user_id).first()
        if gitee_user:
            user = gitee_user.user
            token = user.token
            # context = {"token": token, **UserWithPermSerializer(user).data}
            context = {"token": token}
        else:
            # context = {"token": "", "gitee_user_id": user_id}
            context = {
                "token": "",
                "user_id": user_id,
                "tenant_uuid": tenant_uuid,
                "bind": reverse(
                    "api:gitee:bind",
                    args=[
                        tenant_uuid,
                    ],
                ),
            }

        return context


@extend_schema(tags=["gitee"])
class GiteeUnBindView(GenericAPIView):

    permission_classes = [AllowAny]
    authentication_classes = [ExpiringTokenAuthentication]

    def get(self, request, tenant_uuid):
        """
        解除绑定用户
        """
        tenant = Tenant.objects.filter(uuid=tenant_uuid).first()
        gitee_user = GiteeUser.valid_objects.filter(user=request.user, tenant=tenant).first()
        if gitee_user:
            gitee_user.kill()
            data = {"is_del": True}
        else:
            data = {"is_del": False}
        return Response(data, HTTP_200_OK)


# @extend_schema(tags=["gitee"])
# class GiteeRegisterAndBindView(generics.CreateAPIView):
#     """
#     github账户注册加绑定
#     """

#     permission_classes = []
#     authentication_classes = []

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
