
from rest_framework import serializers


class MarketPlaceExtensionSerializer(serializers.Serializer):

    name = serializers.CharField()
    description = serializers.CharField()
    version = serializers.CharField()
    homepage = serializers.CharField()
    logo = serializers.CharField()
    maintainer = serializers.CharField()
    tags = serializers.CharField()

    # class Meta:

    #     fields = (
    #         'id',
    #         'uuid',
    #         'name',
    #         'url',
    #         'description',
    #     )
