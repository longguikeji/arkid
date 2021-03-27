from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import ExternalIdpBaseSerializer


class GiteeExternalIdpConfigSerializer(serializers.Serializer):
    
    client_id = serializers.CharField()
    secret_id = serializers.CharField()


class GiteeExternalIdpSerializer(ExternalIdpBaseSerializer):

    data = GiteeExternalIdpConfigSerializer(label=_('data'))
