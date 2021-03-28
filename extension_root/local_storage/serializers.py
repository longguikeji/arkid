from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import ExternalIdpBaseSerializer


class LocalStorageConfigSerializer(serializers.Serializer):
    
    data_path = serializers.CharField()


class LocalStorageSerializer(ExternalIdpBaseSerializer):

    data = LocalStorageConfigSerializer(label=_('data'))
