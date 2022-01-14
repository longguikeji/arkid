from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import ExternalIdpBaseSerializer


class WeChatWorkScanBindSerializer(serializers.Serializer):

    user_id = serializers.CharField()


class WeChatWorkScanExternalIdpConfigSerializer(serializers.Serializer):

    agentid = serializers.CharField()
    corpid = serializers.CharField()
    corpsecret = serializers.CharField()

    login_url = serializers.URLField(read_only=True)
    bind_url = serializers.URLField(read_only=True)
    userinfo_url = serializers.URLField(read_only=True)


class WeChatWorkScanExternalIdpSerializer(ExternalIdpBaseSerializer):

    data = WeChatWorkScanExternalIdpConfigSerializer(label=_('data'))
