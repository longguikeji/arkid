from django.http.response import JsonResponse
from rest_framework import generics
from django.utils.translation import gettext_lazy as _
from openapi.utils import extend_schema
from api.v1.serializers.system import SystemConfigSerializer
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from system.models import SystemConfig
from runtime import get_app_runtime
from common.code import Code


@extend_schema(roles=['global admin'], tags=['system'])
class SystemConfigView(generics.RetrieveUpdateAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = SystemConfigSerializer

    def get_object(self):
        systemconfig, is_created = SystemConfig.objects.get_or_create(
            is_del=False,
        )
        if is_created is True:
            systemconfig.data = {
                'is_open_register': True
            }
            systemconfig.save()
        else:
            data = systemconfig.data
            if 'is_open_register' not in data:
                data['is_open_register'] = True
            systemconfig.save()
        return systemconfig

    @extend_schema(roles=['global admin'])
    def update(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return JsonResponse(data={
                'error': Code.PERMISSION_CHECK_ERROR.value,
                'message': _('You are not an administrator.'),
            })
        return super().update(request, *args, **kwargs)
