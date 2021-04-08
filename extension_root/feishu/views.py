from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from config import get_app_config
from .provider import FeishuExternalIdpProvider
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from .user_info_manager import FeishuUserInfoManager, APICallError
from django.http import HttpResponseRedirect
from rest_framework.exceptions import ValidationError
from .constants import AUTHORIZE_URL
from .models import FeishuUser
from django.urls import reverse
import urllib.parse


@extend_schema(tags=["feishu"])
class FeishuLoginView(APIView):

    permission_classes = []
    authentication_classes = []

    def get(self, request, tenant_id):
        c = get_app_config()
        # @TODO: keep other query params

        provider = FeishuExternalIdpProvider()
        provider.load_data(tenant_id=tenant_id)

        next_url = request.GET.get("next", None)
        if next_url is not None:
            next_url = "?next=" + urllib.parse.quote(next_url)
        else:
            next_url = ""
        url = "{}?app_id={}&redirect_uri={}".format(
            AUTHORIZE_URL,
            provider.app_id,
            urllib.parse.quote(
                "{}{}{}".format(
                    c.get_host(),
                    reverse(
                        "api:feishu:callback",
                        args=[
                            tenant_id,
                        ],
                    ),
                    next_url,
                )
            ),
        )

        print(url)

        return HttpResponseRedirect(url)


@extend_schema(tags=["feishu"])
class FeishuCallbackView(APIView):

    permission_classes = []
    authentication_classes = []

    def get(self, request, tenant_id):
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
                provider.load_data(tenant_id=tenant_id)

                user_id = FeishuUserInfoManager(provider.app_id, provider.secret_id, provider._get_token()).get_user_id(code, next_url)
            except APICallError:
                raise ValidationError({"code": ["invalid"]})
        else:
            raise ValidationError({"code": ["required"]})

        context = self.get_token(user_id, tenant_id)
        if next_url:
            next_url = next_url.replace("?next=", "")
            print("****************")
            query_string = urlencode(context)
            url = f"{next_url}?{query_string}"
            url = unquote(url)
            return HttpResponseRedirect(url)

        return Response(context, HTTP_200_OK)

    def get_token(self, user_id, tenant_id):  # pylint: disable=no-self-use
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
                        tenant_id,
                    ],
                ),
            }

        return context
