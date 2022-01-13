from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import ExternalIdpBaseSerializer


class WeChatScanBindSerializer(serializers.Serializer):

    openid = serializers.CharField()


class WeChatScanExternalIdpConfigSerializer(serializers.Serializer):

    appid = serializers.CharField()
    secret = serializers.CharField()

    login_url = serializers.URLField(read_only=True)
    bind_url = serializers.URLField(read_only=True)
    userinfo_url = serializers.URLField(read_only=True)


class WeChatScanExternalIdpSerializer(ExternalIdpBaseSerializer):

    data = WeChatScanExternalIdpConfigSerializer(label=_('data'))
