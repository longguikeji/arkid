from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import ExternalIdpBaseSerializer


class OSSStorageConfigSerializer(serializers.Serializer):
    
    endpoint = serializers.CharField()
    domain = serializers.CharField()
    bucket = serializers.CharField()
    access_key = serializers.CharField()
    secret_key = serializers.CharField()


class OSSStorageSerializer(ExternalIdpBaseSerializer):

    data = OSSStorageConfigSerializer(label=_('data'))
