"""
第三方账号登录视图
"""
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_403_FORBIDDEN, HTTP_201_CREATED, HTTP_200_OK
from rest_framework.views import APIView

from executer.core import CLI
from executer.log.rdb import LOG_CLI
from oneid_meta.models import GithubUser, Group
from oneid_meta.models.config import AccountConfig, GithubConfig
from siteapi.v1.serializers.ucenter import BindSerializer, RegisterAndBindSerializer
from siteapi.v1.serializers.user import UserWithPermSerializer
from thirdparty_data_sdk.error_utils import APICallError
from thirdparty_data_sdk.github_sdk.userinfo_manager import GithubUserInfoManager


def require_github_supported(func):
    """
    检查是否允许github账号登录装饰器
    """
    def inner(self, request):
        return Response({'err_msg': 'github not allowed'}, HTTP_403_FORBIDDEN)\
            if not AccountConfig.get_current().support_github else func(self, request)

    return inner


class GithubBindAPIView(GenericAPIView):
    """
    Github账号绑定
    """
    permission_classes = []
    authentication_classes = []

    serializer_class = BindSerializer

    @require_github_supported
    def post(self, request):
        """
        绑定用户
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        github_user_id = serializer.validated_data['user_id']
        github_user = GithubUser.valid_objects.filter(user=user).first()
        if github_user:
            github_user.github_user_id = github_user_id
        else:
            github_user = GithubUser.valid_objects.create(github_user_id=github_user_id, user=user)
        github_user.save()
        token = user.token
        data = {'token': token, **UserWithPermSerializer(user).data}
        LOG_CLI(user).user_login()
        return Response(data, HTTP_201_CREATED)


class GithubCallbackView(APIView):
    """
    github/callback/
    github用户登录回调页面
    """
    permission_classes = []
    authentication_classes = []

    @require_github_supported
    def get(self, request):
        """
        处理github用户登录之后重定向页面
        """
        code = request.GET['code']
        client_id = GithubConfig.get_current().client_id
        client_secret = GithubConfig.get_current().client_secret
        if code:
            try:
                user_id = GithubUserInfoManager(client_id, client_secret).get_user_id(code)
            except APICallError:
                raise ValidationError({'code': ['invalid']})
        else:
            raise ValidationError({'code': ['required']})
        context = self.get_token(user_id)
        return Response(context, HTTP_200_OK)

    def get_token(self, user_id):    # pylint: disable=no-self-use
        """
        从Github表查询用户，返回token
        """
        github_user = GithubUser.valid_objects.filter(github_user_id=user_id).first()
        if github_user:
            user = github_user.user
            token = user.token
            LOG_CLI(user).user_login()
            context = {'token': token, **UserWithPermSerializer(user).data}
        else:
            context = {'token': '', 'third_party_id': user_id}
        return context


class GithubRegisterAndBindView(generics.CreateAPIView):
    """
    github账户注册加绑定
    """
    permission_classes = []
    authentication_classes = []

    serializer_class = RegisterAndBindSerializer
    read_serializer_class = UserWithPermSerializer

    def create(self, request, *args, **kwargs):
        """
        github账户注册并绑定
        """
        if not AccountConfig.get_current().support_github_register:
            return Response({'err_msg': 'github register not allowed'}, HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)

        cli = CLI(user)
        cli.add_users_to_group([user], Group.get_extern_root())
        data = self.read_serializer_class(user).data
        data.update(token=user.token)
        user_id = serializer.validated_data['user_id']
        github_user = GithubUser.valid_objects.create(github_user_id=user_id, user=user)
        github_user.save()
        return Response(data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        user = serializer.save()
        LOG_CLI(serializer.instance).user_register()
        return user
