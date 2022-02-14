
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _


class ArkStoreExtensionSerializer(serializers.Serializer):

    name = serializers.CharField()
    description = serializers.CharField()
    # version = serializers.CharField()
    # homepage = serializers.CharField()
    # logo = serializers.CharField()
    author = serializers.CharField()
    # tags = serializers.CharField()
    # type = serializers.CharField()
    # scope = serializers.CharField()
    uuid = serializers.UUIDField(default='')
    purchased = serializers.CharField()
