from django.http.response import JsonResponse
from rest_framework.response import Response
from rest_framework import generics
from django.utils.translation import gettext_lazy as _
from openapi.utils import extend_schema
from api.v1.serializers.system import (
    SystemConfigSerializer,
    SystemPrivacyNoticeSerializer,
)
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from system.models import SystemConfig, SystemPrivacyNotice
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
            systemconfig.data = {'is_open_register': True}
            systemconfig.save()
        else:
            data = systemconfig.data
            if 'is_open_register' not in data:
                data['is_open_register'] = True
            systemconfig.save()
        return systemconfig


@extend_schema(roles=['global admin'], tags=['system'])
class SystemPrivacyNoticeView(generics.RetrieveUpdateAPIView):

    permission_classes = [IsAuthenticated, IsSuperAdmin]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = SystemPrivacyNoticeSerializer

    def get_object(self):
        privacy_notice, is_created = SystemPrivacyNotice.objects.get_or_create(
            is_del=False, is_active=True
        )
        return privacy_notice

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = SystemPrivacyNoticeSerializer(instance, data=request.data)
        serializer.is_valid()
        serializer.save()
        return Response(serializer.data)
