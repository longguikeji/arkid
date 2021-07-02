import os
import requests
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
from .models import GiteeUser, GiteeInfo
from urllib.parse import urlencode, unquote
import urllib.parse
from django.urls import reverse
from config import get_app_config
from tenant.models import Tenant
from .constants import AUTHORIZE_URL, FRESH_TOKEN_URL
from drf_spectacular.utils import extend_schema
from .provider import GiteeExternalIdpProvider
from .serializers import GiteeBindSerializer, GiteeDataSerializer

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

        redirect_uri = "{}{}".format(provider.callback_url, next_url)

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
        frontend_host = get_app_config().get_frontend_host().replace('http://' , '').replace('https://' , '')
        if "third_part_callback" not in next_url or frontend_host not in next_url:
            return Response({'error_msg': '错误的跳转页面'}, HTTP_200_OK)
        if next_url is not None:
            next_url = "?next=" + urllib.parse.quote(next_url)
        else:
            next_url = ""
        if code:
            try:
                provider = GiteeExternalIdpProvider()
                provider.load_data(tenant_uuid=tenant_uuid)
                user_id, access_token, refresh_token = GiteeUserInfoManager(
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

        context = self.get_token(user_id, access_token, refresh_token, tenant_uuid)
        if next_url:
            next_url = next_url.replace("?next=", "")
            query_string = urlencode(context)
            url = f"{next_url}?{query_string}"
            url = unquote(url)
            return HttpResponseRedirect(url)

        return Response(context, HTTP_200_OK)

    def get_token(self, user_id, access_token, refresh_token, tenant_uuid):  # pylint: disable=no-self-use
        gitee_user = GiteeUser.valid_objects.filter(gitee_user_id=user_id).first()
        giteeinfo, created = GiteeInfo.objects.get_or_create(
            is_del=False,
            gitee_user_id=user_id,
        )
        giteeinfo.access_token = access_token
        giteeinfo.refresh_token = refresh_token
        giteeinfo.save()
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


@extend_schema(tags=["gitee"])
class GiteeDataView(GenericAPIView):

    permission_classes = [AllowAny]
    authentication_classes = [ExpiringTokenAuthentication]
    serializer_class = GiteeDataSerializer

    def post(self, request, tenant_uuid):
        """
        获取gitee数据
        """
        tenant = Tenant.objects.filter(uuid=tenant_uuid).first()
        gitee_user = GiteeUser.valid_objects.filter(user=request.user, tenant=tenant).first()
        if gitee_user:
            giteeinfo = GiteeInfo.valid_objects.filter(
                gitee_user_id=gitee_user.gitee_user_id
            ).first()
            if not giteeinfo:
                return Response({'error_msg': '该用户没有绑定的giteeinfo'}, HTTP_200_OK)
            url = request.data.pop('url')
            method = request.data.pop('method')
            data = request.data
            headers = {"Authorization": "token " + giteeinfo.access_token}
            params = {"access_token": giteeinfo.access_token}
            params = params.update(data)
            if method == "get":
                response = requests.get(
                    url,
                    params=params,
                    headers=headers,
                )
                if response.status_code == 401:
                    # 401 Unauthorized: Access token is expired
                    response = self.again_get_response(url, giteeinfo, data)
                response = response.json()
            else:
                response = requests.post(
                    url,
                    params=params,
                    headers=headers,
                )
                if response.status_code == 401:
                    # 401 Unauthorized: Access token is expired
                    response = self.again_get_response(url, giteeinfo, data)
                response = response.json()
            return Response(response, HTTP_200_OK)
        else:
            return Response({'error_msg': '该用户没有绑定的gitee'}, HTTP_200_OK)


    def again_get_response(self, url, giteeinfo, data):
        self.refresh_token(giteeinfo)
        headers = {"Authorization": "token " + giteeinfo.access_token}
        params = {"access_token": giteeinfo.access_token}
        params = params.update(data)
        response = requests.get(
            url,
            params=params,
            headers=headers,
        )
        return response


    def refresh_token(self, giteeinfo):
        fresh_url = FRESH_TOKEN_URL.format(giteeinfo.refresh_token)
        fresh_response = requests.post(fresh_url)
        fresh_response = fresh_response.json()
        # fresh_response = {
        #     "access_token":"b517256123159fd34d992511ff83c567",
        #     "token_type":"bearer",
        #     "expires_in":86400,
        #     "refresh_token":"356fd83639a5758b05ccb92b343e3aac5039a3ae19bf54a28be837e896a98762",
        #     "scope":"user_info projects pull_requests issues notes keys hook groups gists enterprises emails",
        #     "created_at":1622084590
        # }
        access_token = fresh_response.get('access_token', None)
        refresh_token = fresh_response.get('refresh_token', None)
        if access_token:
            giteeinfo.access_token = access_token
        if refresh_token:
            giteeinfo.refresh_token = refresh_token
        giteeinfo.save()

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
