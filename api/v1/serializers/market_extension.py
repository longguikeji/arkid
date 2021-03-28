from rest_framework.utils import serializer_helpers
from common.serializer import BaseDynamicFieldModelSerializer
from rest_framework import serializers
from common.extension import InMemExtension

class MarketPlaceExtensionSerializer(serializers.Serializer):

    name = serializers.CharField()
    description = serializers.CharField()
    version = serializers.CharField()
    homepage = serializers.CharField()
    logo = serializers.CharField()
    maintainer = serializers.CharField()

    # class Meta:

    #     fields = (
    #         'id',
    #         'uuid',
    #         'name',
    #         'url',
    #         'description',
    #     )
