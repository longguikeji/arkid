from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import ExternalIdpBaseSerializer


class GiteeBindSerializer(serializers.Serializer):

    user_id = serializers.CharField()


class GiteeExternalIdpConfigSerializer(serializers.Serializer):

    client_id = serializers.CharField()
    secret_id = serializers.CharField()

    login_url = serializers.URLField(read_only=True)
    callback_url = serializers.URLField(read_only=True)
    bind_url = serializers.URLField(read_only=True)
    img_url = serializers.URLField(read_only=True)


class GiteeExternalIdpSerializer(ExternalIdpBaseSerializer):

    data = GiteeExternalIdpConfigSerializer(label=_('data'))
