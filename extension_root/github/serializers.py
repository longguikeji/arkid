from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import ExternalIdpBaseSerializer


class GithubExternalIdpConfigSerializer(serializers.Serializer):
    
    client_id = serializers.CharField()
    secret_id = serializers.CharField()

    login_url = serializers.URLField(read_only=True)
    callback_url = serializers.URLField(read_only=True)
    bind_url = serializers.URLField(read_only=True)

class GithubExternalIdpSerializer(ExternalIdpBaseSerializer):

    data = GithubExternalIdpConfigSerializer(label=_('data'))
