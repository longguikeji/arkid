from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import ExtensionBaseSerializer

class MessageExtensionConfigSerializer(serializers.Serializer):

    host = serializers.CharField(required=True, label=_('服务IP'))
    port = serializers.CharField(required=True, label=_('端口号'))
    username = serializers.CharField(required=True, label=_('用户名'))
    password = serializers.CharField(required=True, label=_('密码'))
    destination = serializers.CharField(required=True,label=_("队列名"))


class MessageExtensionSerializer(ExtensionBaseSerializer):

    data = MessageExtensionConfigSerializer(label=_('配置数据'))
    