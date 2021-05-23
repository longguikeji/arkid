from common.provider import AppTypeProvider
from app.models import App
from common.serializer import BaseDynamicFieldModelSerializer
from rest_framework import serializers
from runtime import get_app_runtime
from drf_spectacular.utils import extend_schema
from inventory.models import Permission
from django.contrib.contenttypes.models import ContentType
from provisioning.models import Config
from schema.models import Schema


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
        )


class AppProvisioningShemasSerializer(AppSerializer):
    class Meta:
        model = Schema

        fields = (
            'name',
            'description',
            'mapping_type',
            'default_value_if_is_none',
            'source_attribute',
            'target_attribute',
            'is_used_matching',
            'matching_precedence',
            'constant_value',
            'scim_path',
            'sub_attrs',
        )


class AppProvisioningSerializer(BaseDynamicFieldModelSerializer):
    schemas = AppProvisioningShemasSerializer(many=True)

    class Meta:
        model = Config

        fields = (
            'endpoint',
            'token',
            'schemas',
            'mode',
            'status',
            'username',
            'password',
        )

    def create(self, validated_data):
        app = self.context['app']

        endpoint = validated_data.pop('endpoint')
        token = validated_data.pop('token')
        mode = validated_data.pop('mode', 0)
        status = validated_data.pop('status', 1)
        username = validated_data.pop('username')
        password = validated_data.pop('password')

        schemas = validated_data.pop('schemas', [])

        provision = Config.objects.create(
            app=app,
            endpoint=endpoint,
            token=token,
            mode=mode,
            status=status,
            username=username,
            password=password,
        )

        for sch in schemas:
            obj = Schema.objects.create(
                name=sch.get('name', ''),
                description=sch.get('mapping_type', 0),
                default_value_if_is_none=sch.get('default_value_if_is_none', ''),
                source_attribute=sch.get('source_attribute', ''),
                target_attribute=sch.get('target_attribute', ''),
                is_used_matching=sch.get('is_used_matching', False),
                matching_precedence=sch.get('matching_precedence', -1),
                constant_value=sch.get('constant_value', ''),
                scim_path=sch.get('scim_path', ''),
                sub_attrs=sch.get('sub_attrs', {}),
            )
            provision.schemas.add(obj)
        provision.save()

        return provision
