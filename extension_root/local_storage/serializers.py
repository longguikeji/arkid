from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import ExtensionBaseSerializer


class LocalStorageConfigSerializer(serializers.Serializer):
    
    data_path = serializers.CharField()


class LocalStorageSerializer(ExtensionBaseSerializer):

    data = LocalStorageConfigSerializer(label=_('data'))
