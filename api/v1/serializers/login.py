from tenant.models import Tenant
from rest_framework import serializers
from common.serializer import BaseDynamicFieldModelSerializer
from drf_spectacular.utils import extend_schema_field
from .tenant import TenantSerializer
from django.utils.translation import gettext_lazy as _


class TSerializer(serializers.Serializer):

    token = serializers.CharField(read_only=True)
    tenants = serializers.ListField(child=TenantSerializer())

    class Meta:

        fields = ('token',)


class LoginSerializer(serializers.Serializer):

    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    error = serializers.CharField(read_only=True)
    data = TSerializer(read_only=True)

    class Meta:

        fields = (
            'username',
            'password',
        )


class UserNameRegisterRequestSerializer(serializers.Serializer):

    username = serializers.CharField(label=_('用户名'))
    password = serializers.CharField(label=_('密码'))


class MobileRegisterRequestSerializer(serializers.Serializer):

    mobile = serializers.CharField(label=_('手机号'))
    code = serializers.CharField(label=_('验证码'))
    password = serializers.CharField(label=_('密码'))


class UserNameLoginRequestSerializer(serializers.Serializer):

    username = serializers.CharField(label=_('用户名'))
    password = serializers.CharField(label=_('密码'))
    code = serializers.CharField(label=_('图片验证码'), required=False)
    code_filename = serializers.CharField(label=_('图片验证码的文件名称'), required=False)
