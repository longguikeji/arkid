from rest_framework import serializers
from django.utils.translation import gettext_lazy as _


class AuthCodeSerializer(serializers.Serializer):

    file_name = serializers.CharField(label=_('文件名'))
    code = serializers.CharField(label=_('用户输入的验证码'))


class AuthCodeResponseSerializer(serializers.Serializer):

    key = serializers.CharField(label=_('图片名称'))
    base64 = serializers.CharField(label=_('图片base64'))

class AuthCodeCheckResponseSerializer(serializers.Serializer):

    is_succeed = serializers.BooleanField(label=_('是否正确'))
