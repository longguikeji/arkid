from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import OtherAuthFactorBaseSerializer


class AuthCodeConfigDataSerializer(serializers.Serializer):

    auth_code_length = serializers.IntegerField(default=4, label=_('验证码位数'))


class AuthCodeConfigSerializer(OtherAuthFactorBaseSerializer):

    data = AuthCodeConfigDataSerializer(label=_('配置数据'))
