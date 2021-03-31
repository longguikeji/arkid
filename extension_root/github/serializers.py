from rest_framework import serializers
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from common.serializer import ExternalIdpBaseSerializer


class GithubExternalIdpConfigSerializer(serializers.Serializer):

    client_id = serializers.CharField()
    secret_id = serializers.CharField()
    login_url = serializers.CharField(read_only=True)
    img_url = serializers.CharField(read_only=True)


class GithubExternalIdpSerializer(ExternalIdpBaseSerializer):

    data = GithubExternalIdpConfigSerializer(label=_("data"))
