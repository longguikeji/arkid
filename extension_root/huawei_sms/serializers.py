from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import ExtensionBaseSerializer


class HuaWeiSMSConfigSerializer(serializers.Serializer):

    access_key = serializers.CharField(required=True, label=_('Access Key'))
    secret_key = serializers.CharField(required=True, label=_('Secret Key'))
    template = serializers.CharField(required=True, label=_('Template'))
    signature = serializers.CharField(required=True, label=_('Signature'))
    sender = serializers.CharField(required=True, label=_('Sender'))


class HuaWeiSMSSerializer(ExtensionBaseSerializer):

    data = HuaWeiSMSConfigSerializer(label=_('data'))
