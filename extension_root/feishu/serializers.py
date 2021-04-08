from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import ExternalIdpBaseSerializer


class FeiShuExternalIdpConfigSerializer(serializers.Serializer):

    app_id = serializers.CharField()
    secret_id = serializers.CharField()


class FeishuExternalIdpSerializer(ExternalIdpBaseSerializer):

    data = FeiShuExternalIdpConfigSerializer(label=_('data'))
