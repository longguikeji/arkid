from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import ExternalIdpBaseSerializer


class MiniProgramExternalIdpConfigSerializer(serializers.Serializer):

    app_id = serializers.CharField()
    secret_id = serializers.CharField()

    login_url = serializers.URLField(read_only=True)
    bind_url = serializers.URLField(read_only=True)


class MiniProgramBindSerializer(serializers.Serializer):

    user_id = serializers.CharField()
    name = serializers.CharField()
    avatar = serializers.CharField()


class MiniProgramExternalIdpSerializer(ExternalIdpBaseSerializer):

    data = MiniProgramExternalIdpConfigSerializer(label=_('data'))
