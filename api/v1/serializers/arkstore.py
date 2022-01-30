
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _


class MarketPlaceExtensionSerializer(serializers.Serializer):

    name = serializers.CharField()
    description = serializers.CharField()
    version = serializers.CharField()
    homepage = serializers.CharField()
    logo = serializers.CharField()
    maintainer = serializers.CharField()
    tags = serializers.CharField()
    type = serializers.CharField()
    scope = serializers.CharField()
    uuid = serializers.UUIDField(default='')
    purchased = serializers.CharField()
