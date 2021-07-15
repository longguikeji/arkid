from extension.models import Extension
from common.serializer import BaseDynamicFieldModelSerializer
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from extension.utils import reload_extension


class ExtensionSerializer(BaseDynamicFieldModelSerializer):

    description = serializers.CharField(source='inmem.description', read_only=True)
    version = serializers.CharField(source='inmem.version', read_only=True)
    homepage = serializers.CharField(source='inmem.homepage', read_only=True)
    logo = serializers.CharField(source='inmem.logo', read_only=True)
    maintainer = serializers.CharField(source='inmem.maintainer', read_only=True)
    is_active = serializers.BooleanField(label=_('是否启用'))

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
            'is_active',
            'data',
        )

    def create(self, validated_data):
        extension_type = validated_data.pop('type', None)
        assert extension_type is not None

        o, _ = Extension.objects.get_or_create(
            is_del=False,
            type=extension_type
        )
        o.is_active = validated_data.get('is_active')
        o.is_del = False
        o.data = validated_data.get('data')
        o.save()
        reload_extension(o.type, o.is_active)
        return o

    def update(self, instance, validated_data):
        instance.__dict__.update(validated_data)
        instance.save()
        reload_extension(instance.type, instance.is_active)
        return instance


class ExtensionListSerializer(ExtensionSerializer):

    class Meta:
        model = Extension

        fields = (
            'type',
        )
