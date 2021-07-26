from django.http.response import JsonResponse
from rest_framework import generics
from django.utils.translation import gettext_lazy as _
from openapi.utils import extend_schema
from api.v1.serializers.system import (
    SystemConfigSerializer,
    LoginRegisterConfigSerializer,
    PrivacyNoticeConfigSerializer,
)
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response
from system.models import SystemConfig
from system.permission import IsSuperAdmin
from runtime import get_app_runtime
from common.code import Code
from drf_spectacular.utils import PolymorphicProxySerializer

SystemConfigPolymorphicProxySerializer = PolymorphicProxySerializer(
    component_name='SystemConfigPolymorphicProxySerializer',
    serializers={
        'login_register': LoginRegisterConfigSerializer,
        'privacy_notice': PrivacyNoticeConfigSerializer,
    },
    resource_type_field_name='subject',
)


@extend_schema(
    roles=['global admin'],
    tags=['system'],
    request=SystemConfigPolymorphicProxySerializer,
    responses=SystemConfigPolymorphicProxySerializer,
)
class SystemConfigView(generics.RetrieveUpdateAPIView):

    permission_classes = [IsAuthenticated, IsSuperAdmin]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = SystemConfigSerializer

    def get_serializer_class(self):
        if 'subject' not in self.kwargs:
            return SystemConfigSerializer

        subject = self.kwargs.get('subject')

        if subject == 'login_register':
            return LoginRegisterConfigSerializer

        if subject == 'privacy_notice':
            return PrivacyNoticeConfigSerializer

        raise NotFound

    def get_object(self):
        systemconfig, is_created = SystemConfig.objects.get_or_create(
            is_del=False,
        )
        if is_created is True:
            # 初始化配置
            pass
        return systemconfig

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = SystemConfigSerializer(instance)
        data = serializer.data
        subject = self.kwargs.get('subject', '')
        if subject:
            data = data.get('data')
            return Response(data.get(subject))
        else:
            return Response(data.get('data'))

    def update(self, request, *args, **kwargs):
        subject = self.kwargs.get('subject', '')
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(instance=instance, subject=subject)
        data = instance.data
        if subject:
            return Response(data.get(subject))
        else:
            return Response(data)
