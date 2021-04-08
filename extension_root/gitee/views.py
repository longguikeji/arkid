import os
from rest_framework.views import APIView
from django.http import HttpResponseRedirect
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from .user_info_manager import GiteeUserInfoManager, APICallError
from .models import GiteeUser
from urllib.parse import urlencode, unquote
import urllib.parse
from django.urls import reverse
from config import get_app_config
from .constants import AUTHORIZE_URL
from drf_spectacular.utils import extend_schema
from .provider import GiteeExternalIdpProvider

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


@extend_schema(tags=["gitee"])
class GiteeLoginView(APIView):

    permission_classes = []
    authentication_classes = []

    def get(self, request, tenant_id):
        c = get_app_config()
        # @TODO: keep other query params

        provider = GiteeExternalIdpProvider()
        provider.load_data(tenant_id=tenant_id)

        next_url = request.GET.get("next", None)
        if next_url is not None:
            next_url = "?next=" + urllib.parse.quote(next_url)
        else:
            next_url = ""
        redirect_uri = "{}{}{}".format( c.get_host(), provider.callback_url, next_url )
        url = "{}?client_id={}&redirect_uri={}&response_type=code&scope=user_info".format(
            AUTHORIZE_URL,
            provider.client_id,
            urllib.parse.quote( redirect_uri ),
            # request.GET.get("redirect_uri"),
        )

        print(url)

        return HttpResponseRedirect(url)


@extend_schema(tags=["gitee"])
class GiteeBindAPIView(GenericAPIView):

    permission_classes = []
    authentication_classes = []

    # serializer_class = BindSerializer

    # def post(self, request):
    #     """
    #     绑定用户
    #     """
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     user = serializer.validated_data['user']
    #     github_user_id = serializer.validated_data['user_id']
    #     github_user = GithubUser.valid_objects.filter(user=user).first()
    #     if github_user:
    #         github_user.github_user_id = github_user_id
    #     else:
    #         github_user = GithubUser.valid_objects.create(github_user_id=github_user_id, user=user)
    #     github_user.save()
    #     token = user.token
    #     data = {'token': token, **UserWithPermSerializer(user).data}
    #     LOG_CLI(user).user_login()
    #     return Response(data, HTTP_201_CREATED)


@extend_schema(tags=["gitee"])
class GiteeCallbackView(APIView):

    permission_classes = []
    authentication_classes = []

    def get(self, request, tenant_id):
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
                provider.load_data(tenant_id=tenant_id)
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
                raise ValidationError({"code": ["invalid"],"message": error})
        else:
            raise ValidationError({"code": ["required"]})

        context = self.get_token(user_id, tenant_id)
        if next_url:
            next_url = next_url.replace("?next=", "")
            query_string = urlencode(context)
            url = f"{next_url}?{query_string}"
            url = unquote(url)
            return HttpResponseRedirect(url)

        return Response(context, HTTP_200_OK)

    def get_token(self, user_id, tenant_id):  # pylint: disable=no-self-use
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
                "tenant_id": tenant_id,
                "bind": reverse(
                    "api:gitee:bind",
                    args=[
                        tenant_id,
                    ],
                ),
            }

        return context


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
