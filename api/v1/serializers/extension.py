from extension.models import Extension
from rest_framework.utils import serializer_helpers
from common.serializer import BaseDynamicFieldModelSerializer
from rest_framework import serializers
from common.extension import InMemExtension

class ExtensionSerializer(BaseDynamicFieldModelSerializer):

    description = serializers.CharField(source='inmem.description', read_only=True)
    version = serializers.CharField(source='inmem.version', read_only=True)
    homepage = serializers.CharField(source='inmem.homepage', read_only=True)
    logo = serializers.CharField(source='inmem.logo', read_only=True)
    maintainer = serializers.CharField(source='inmem.maintainer', read_only=True)

    class Meta:

        model = Extension

        fields = (
            'uuid',
            'type',
            'description',
            'version',
            'homepage',
            'logo',
            'maintainer',
            'data',
        )

    def create(self, validated_data):
        extension_type = validated_data.pop('type', None)
        assert extension_type is not None        

        o, _ = Extension.active_objects.get_or_create(
            type=extension_type
        )

        o.is_del = False
        o.data = validated_data.get('data')
        o.save()
        return o

class ExtensionListSerializer(ExtensionSerializer):

    class Meta:
        model = Extension

        fields = (
            'type',
        )