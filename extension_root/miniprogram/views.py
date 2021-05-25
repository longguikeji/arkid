from drf_spectacular.utils import extend_schema
from django.urls import reverse
from rest_framework.generics import GenericAPIView
from .provider import MiniProgramExternalIdpProvider
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from .user_info_manager import MiniProgramUserInfoManager, APICallError
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from .serializers import(
    MiniProgramBindSerializer, MiniProgramLoginSerializer, MiniProgramLoginResponseSerializer,
    MiniProgramBindResponseSerializer,
)
from .models import MiniProgramUser
from tenant.models import Tenant


@extend_schema(tags=["miniprogram"])
class MiniProgramLoginView(GenericAPIView):

    permission_classes = []
    authentication_classes = []
    serializer_class = MiniProgramLoginSerializer

    @extend_schema(responses=MiniProgramLoginResponseSerializer)
    def post(self, request, tenant_uuid):
        '''
        处理miniprogram用户登录
        '''
        code = request.data.get("code")
        name = request.data.get("name")
        avatar = request.data.get("avatar")
        if code:
            try:
                provider = MiniProgramExternalIdpProvider()
                provider.load_data(tenant_uuid=tenant_uuid)

                user_id = MiniProgramUserInfoManager(provider.app_id, provider.secret_id).get_user_id(code)
            except APICallError:
                raise ValidationError({"code": ["invalid"]})
        else:
            raise ValidationError({"code": ["required"]})

        context = self.get_token(tenant_uuid, user_id, name, avatar)
        return Response(context, HTTP_200_OK)

    def get_token(self, tenant_uuid, user_id, name, avatar):  # pylint: disable=no-self-use
        miniprogram_user = MiniProgramUser.valid_objects.filter(miniprogram_user_id=user_id).first()
        if miniprogram_user:
            miniprogram_user.name = name
            miniprogram_user.avatar = avatar
            user = miniprogram_user.user
            token = user.token
            context = {"token": token}
        else:
            context = {
                "token": "",
                "user_id": user_id,
                'name': name,
                'avatar': avatar,
                "tenant_uuid": tenant_uuid,
                "bind": reverse(
                    "api:miniprogram:bind",
                    args=[
                        tenant_uuid,
                    ],
                ),
            }
        return context


@extend_schema(tags=["miniprogram"])
class MiniProgramBindAPIView(GenericAPIView):
    """
    MiniProgram账号绑定
    """

    permission_classes = [AllowAny]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = MiniProgramBindSerializer

    @extend_schema(responses=MiniProgramBindResponseSerializer)
    def post(self, request, tenant_uuid):
        """
        绑定用户
        """
        tenant = Tenant.objects.filter(uuid=tenant_uuid).first()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        miniprogram_user_id = serializer.validated_data['user_id']
        name = serializer.validated_data['name']
        avatar = serializer.validated_data['avatar']

        miniprogram_user = MiniProgramUser.valid_objects.filter(user=user, tenant=tenant).first()
        if miniprogram_user:
            miniprogram_user.miniprogram_user_id = miniprogram_user_id
            miniprogram_user.save()
        else:
            miniprogram_user = MiniProgramUser.valid_objects.create(
                miniprogram_user_id=miniprogram_user_id, user=user, tenant=tenant, name=name, avatar=avatar
            )
        token = user.token
        data = {"token": token}
        return Response(data, HTTP_200_OK)


@extend_schema(tags=["miniprogram"])
class MiniProgramUnBindAPIView(GenericAPIView):

    permission_classes = [AllowAny]
    authentication_classes = [ExpiringTokenAuthentication]

    def get(self, request, tenant_uuid):
        """
        解除绑定用户
        """
        tenant = Tenant.objects.filter(uuid=tenant_uuid).first()
        miniprogramuser = MiniProgramUser.valid_objects.filter(user=request.user, tenant=tenant).first()
        if miniprogramuser:
            miniprogramuser.kill()
            data = {"is_del": True}
        else:
            data = {"is_del": False}
        return Response(data, HTTP_200_OK)
