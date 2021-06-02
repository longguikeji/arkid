from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import ExtensionBaseSerializer


class AuthCodeConfigSerializer(serializers.Serializer):

    upload_file_path = serializers.CharField(label=_('验证码保存路径'))


class AuthCodeInfoSerializer(ExtensionBaseSerializer):

    data = AuthCodeConfigSerializer(label=_('data'))
