from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import LoginRegisterConfigBaseSerializer
from api.v1.fields.custom import create_password_field


class PasswordLoginRegisterConfigDataSerializer(serializers.Serializer):

    login_enabled = serializers.BooleanField(default=True, label=_('启用登录'))
    register_enabled = serializers.BooleanField(default=True, label=_('启用注册'))


class PasswordLoginRegisterConfigSerializer(LoginRegisterConfigBaseSerializer):

    data = PasswordLoginRegisterConfigDataSerializer(label=_('配置数据'))


class PasswordLoginResponseSerializer(serializers.Serializer):

    token = serializers.CharField(label=_('token'))


class PasswordRegisterResponseSerializer(serializers.Serializer):

    token = serializers.CharField(label=_('token'))
