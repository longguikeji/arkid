from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import ExternalIdpBaseSerializer


class FeiShuExternalIdpConfigSerializer(serializers.Serializer):

    app_id = serializers.CharField()
    secret_id = serializers.CharField()

    login_url = serializers.URLField(read_only=True)
    callback_url = serializers.URLField(read_only=True)
    bind_url = serializers.URLField(read_only=True)

class FeishuExternalIdpSerializer(ExternalIdpBaseSerializer):

    data = FeiShuExternalIdpConfigSerializer(label=_('data'))
