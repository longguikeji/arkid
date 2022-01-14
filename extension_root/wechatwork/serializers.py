from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import ExternalIdpBaseSerializer


class WeChatWorkBindSerializer(serializers.Serializer):

    user_id = serializers.CharField()


class WeChatWorkExternalIdpConfigSerializer(serializers.Serializer):

    corpid = serializers.CharField()
    corpsecret = serializers.CharField()

    login_url = serializers.URLField(read_only=True)
    bind_url = serializers.URLField(read_only=True)
    userinfo_url = serializers.URLField(read_only=True)


class WeChatWorkExternalIdpSerializer(ExternalIdpBaseSerializer):

    data = WeChatWorkExternalIdpConfigSerializer(label=_('data'))
