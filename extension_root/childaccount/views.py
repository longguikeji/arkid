from drf_spectacular.utils import extend_schema
from common.code import Code
from django.urls import reverse
from rest_framework.generics import GenericAPIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from django.http.response import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.http.response import JsonResponse
from common.paginator import DefaultListPaginator
from rest_framework.permissions import IsAuthenticated
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from openapi.utils import extend_schema
from extension_root.childaccount.serializers import(
    ChildUserSerializer, ChildUserCheckTypeSerializer, ChildUserGetTokenSerializer,
)
from inventory.models import User


@extend_schema(roles=['generaluser', 'tenantadmin', 'globaladmin'], tags=['user'])
class ChildUserAccountListView(generics.ListCreateAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = ChildUserSerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        user = self.request.user
        result = []
        if user.parent:
            parent = user.parent
            result.append(parent)
            users = User.active_objects.filter(parent=parent)
            for user in users:
                result.append(user)
        else:
            result.append(user)
            users = User.active_objects.filter(parent=user)
            for user in users:
                result.append(user)
        return result

    def check_password(self, pwd):
        if pwd.isdigit() or len(pwd) < 8:
            return False
        return True

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        email = request.data.get('email')
        mobile = request.data.get('mobile')
        password = request.data.get('password')
        if password and self.check_password(password) is False:
            return JsonResponse(
                data={
                    'error': Code.PASSWORD_STRENGTH_ERROR.value,
                    'message': _('password strength not enough'),
                }
            )
        user_username = User.objects.filter(username=username).exists()
        if user_username:
            return JsonResponse(
                data={
                    'error': Code.USERNAME_EXISTS_ERROR.value,
                    'message': _('username already exists'),
                }
            )
        user_email = User.objects.filter(email=email).exists()
        if user_email:
            return JsonResponse(
                data={
                    'error': Code.EMAIL_EXISTS_ERROR.value,
                    'message': _('email already exists'),
                }
            )
        user_mobile = User.objects.filter(mobile=mobile).exists()
        if user_mobile:
            return JsonResponse(
                data={
                    'error': Code.MOBILE_EXISTS_ERROR.value,
                    'message': _('mobile already exists'),
                }
            )
        return super(ChildUserAccountListView, self).create(request, *args, **kwargs)


@extend_schema(roles=['generaluser', 'tenantadmin', 'globaladmin'], tags=['user'])
class ChildUserAccountDetailView(generics.RetrieveUpdateDestroyAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = ChildUserSerializer

    def get_object(self):
        account_uuid = self.kwargs['account_uuid']
        return User.active_objects.filter(uuid=account_uuid).first()

    def check_password(self, pwd):
        if pwd.isdigit() or len(pwd) < 8:
            return False
        return True

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        username = request.data.get('username')
        email = request.data.get('email')
        mobile = request.data.get('mobile')
        password = request.data.get('password')
        if password and self.check_password(password) is False:
            return JsonResponse(
                data={
                    'error': Code.PASSWORD_STRENGTH_ERROR.value,
                    'message': _('password strength not enough'),
                }
            )
        user_username = User.objects.filter(username=username).exists()
        if user_username and username != user.username:
            return JsonResponse(
                data={
                    'error': Code.USERNAME_EXISTS_ERROR.value,
                    'message': _('username already exists'),
                }
            )
        user_email = User.objects.filter(email=email).exists()
        if user_email and email != user.email:
            return JsonResponse(
                data={
                    'error': Code.EMAIL_EXISTS_ERROR.value,
                    'message': _('email already exists'),
                }
            )
        user_mobile = User.objects.filter(mobile=mobile).exists()
        if user_mobile and mobile != user.mobile:
            return JsonResponse(
                data={
                    'error': Code.MOBILE_EXISTS_ERROR.value,
                    'message': _('mobile already exists'),
                }
            )
        return super(ChildUserAccountDetailView, self).update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.kill()
        return Response(status=HTTP_204_NO_CONTENT)


@extend_schema(roles=['generaluser', 'tenantadmin', 'globaladmin'], tags=['user'])
class ChildUserAccountCheckTypeView(generics.RetrieveAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = ChildUserCheckTypeSerializer

    @extend_schema(responses=ChildUserCheckTypeSerializer)
    def get(self, request, account_uuid):
        user = User.active_objects.filter(uuid=account_uuid).first()
        if user.parent:
            # 切换成子账号
            parent = user.parent
            # 取得它所有的兄弟子账号
            siblings_users = User.active_objects.filter(parent=parent).exclude(uuid=user.uuid_hex)
            # 兄弟姐妹的parent切为当前账户
            for siblings_user in siblings_users:
                siblings_user.parent = user
                siblings_user.save()
            # 原来父账号的parent改为当前用户
            parent.parent = user
            parent.save()
            # 当前用户的parent清空
            user.parent = None
            user.save()
        serializer = self.get_serializer(
            {
                'is_success': True
            }
        )
        return Response(serializer.data)


@extend_schema(roles=['generaluser', 'tenantadmin', 'globaladmin'], tags=['user'])
class ChildUserAccountGetTokenView(generics.RetrieveAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = ChildUserGetTokenSerializer

    @extend_schema(responses=ChildUserGetTokenSerializer)
    def get(self, request, account_uuid):
        user = request.user
        target_user = User.active_objects.filter(uuid=account_uuid).first()
        token = ''
        if user.uuid == target_user.uuid:
            # 本身
            token = user.token
        elif user.parent == None and target_user.parent == user:
            # 子节点
            token_obj = target_user.refresh_token()
            token = token_obj.key
        elif user.parent == target_user.parent:
            # 兄弟节点
            token_obj = target_user.refresh_token()
            token = token_obj.key
        elif user.parent == target_user:
            # 父节点
            token_obj = target_user.refresh_token()
            token = token_obj.key
        serializer = self.get_serializer(
            {
                'token': token
            }
        )
        return Response(serializer.data)


    
