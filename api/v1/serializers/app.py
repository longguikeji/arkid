from common.provider import AppTypeProvider
from app.models import App
from common.serializer import BaseDynamicFieldModelSerializer
from rest_framework import serializers
from runtime import get_app_runtime
from drf_spectacular.utils import extend_schema
from inventory.models import Permission
from django.contrib.contenttypes.models import ContentType


class AppBaseInfoSerializer(BaseDynamicFieldModelSerializer):

    class Meta:
        model = App

        fields = (
            'uuid',
            'name',
            'logo',
            'url',
            'description',
        )


class AppSerializer(BaseDynamicFieldModelSerializer):

    class Meta:
        model = App

        fields = (
            'uuid',
            'name',
            'url',
            'type',
            'data',
            'description',
        )

        extra_kwargs = {
            'uuid': {'read_only': True},
        }

    def create(self, validated_data):
        tenant = self.context['tenant']

        name = validated_data.pop('name')
        protocol_type = validated_data.pop('type')
        url = validated_data.pop('url', '')
        description = validated_data.pop('description', '')

        protocol_data = validated_data.pop('data', None)

        app = App.objects.create(
            tenant=tenant,
            name=name,
            type=protocol_type,
            url=url,
            description=description,
        )

        r = get_app_runtime()
        provider_cls: AppTypeProvider = r.app_type_providers.get(protocol_type, None)
        assert provider_cls is not None
        provider = provider_cls()
        data = provider.create(app=app, data=protocol_data)
        print(1111,app.url)
        if data is not None:
            app.data = data
            app.save()
        return app

    def update(self, instance, validated_data):
        protocol_type = validated_data.pop('type')
        protocol_data = validated_data.pop('data', None)
        app = instance
        r = get_app_runtime()
        provider_cls: AppTypeProvider = r.app_type_providers.get(protocol_type, None)
        assert provider_cls is not None
        provider = provider_cls()
        data = provider.update(app=app, data=protocol_data)
        if data is not None:
            app.data = data
            app.save()
        instance.__dict__.update(validated_data)
        instance.save()
        return instance


class AppListSerializer(AppSerializer):

    class Meta:
        model = App

        fields = (
            'name',
            'url',
            'type',
            'description',
            'auth_tmpl',
        )

class AddAuthTmplSerializer(serializers.Serializer):

    uuid = serializers.CharField(write_only=True)
    html = serializers.CharField(write_only=True)
    error = serializers.CharField(read_only=True)
    message = serializers.CharField(read_only=True)
