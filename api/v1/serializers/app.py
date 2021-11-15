from common.provider import AppTypeProvider
from app.models import App
from common.serializer import BaseDynamicFieldModelSerializer
from rest_framework import serializers
from runtime import get_app_runtime
from drf_spectacular.utils import extend_schema
from inventory.models import Permission
from django.contrib.contenttypes.models import ContentType
from provisioning.models import Config
from schema.models import Schema, AppProfile
from webhook.manager import WebhookManager
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from api.v1.fields.custom import (
    create_upload_url_field,
)

class AppBaseInfoSerializer(BaseDynamicFieldModelSerializer):

    logo = create_upload_url_field(serializers.URLField)(
        hint=_("请选择图标"), required=False
    )

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
            'logo',
            'type',
            'data',
            'description',
        )

        extra_kwargs = {
            'uuid': {'read_only': True},
        }

    @transaction.atomic()
    def create(self, validated_data):
        tenant = self.context['tenant']

        name = validated_data.pop('name')
        logo = validated_data.pop('logo', '')
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
            logo=logo,
        )

        r = get_app_runtime()
        provider_cls: AppTypeProvider = r.app_type_providers.get(protocol_type, None)
        assert provider_cls is not None
        provider = provider_cls()
        data = provider.create(app=app, data=protocol_data)
        if data is not None:
            app.data = data
            app.save()
        transaction.on_commit(
            lambda: WebhookManager.app_created(self.context['tenant'].uuid, app)
        )
        return app

    @transaction.atomic()
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
        transaction.on_commit(
            lambda: WebhookManager.app_updated(self.context['tenant'].uuid, instance)
        )
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

class AppProvisioningMappingSerializer(BaseDynamicFieldModelSerializer):
    class Meta:
        model = Schema

        fields = (
            'uuid',
            'mapping_type',
            'default_value',
            'source_attribute',
            'target_attribute',
            'is_used_matching',
            'matching_precedence',
            'constant_value',
            'apply_type',
        )

    def create(self, validated_data):
        request = self.context['request']
        app_uuid = request.parser_context.get('kwargs').get('app_uuid')
        app = App.valid_objects.filter(uuid=app_uuid).first()
        config = Config.valid_objects.filter(app=app).first()

        mapping_type = validated_data.get('mapping_type', 'direct')
        default_value = validated_data.get('default_value', '')
        source_attribute = validated_data.get('source_attribute', '')
        target_attribute = validated_data.get('target_attribute', '')
        is_used_matching = validated_data.get('is_used_matching', False)
        constant_value = validated_data.get('constant_value', '')
        apply_type = validated_data.get('apply_type', 'always')

        mapping = Schema.valid_objects.create(
            provisioning_config=config,
            mapping_type=mapping_type,
            default_value=default_value,
            source_attribute=source_attribute,
            target_attribute=target_attribute,
            is_used_matching=is_used_matching,
            constant_value=constant_value,
            apply_type=apply_type,
        )
        return mapping


class AppProvisioningProfileSerializer(BaseDynamicFieldModelSerializer):
    class Meta:
        model = AppProfile

        fields = (
            'uuid',
            'name',
            'type',
            'is_primary',
            'is_required',
            'multi_value',
            'exact_case',
        )

    def create(self, validated_data):
        request = self.context['request']
        app_uuid = request.parser_context.get('kwargs').get('app_uuid')
        app = App.valid_objects.filter(uuid=app_uuid).first()
        config = Config.valid_objects.filter(app=app).first()

        name = validated_data.get('name', '')
        type = validated_data.get('type', 'string')
        is_primary = validated_data.get('is_primary', False)
        is_required = validated_data.get('is_required', False)
        multi_value = validated_data.get('multi_value', False)
        exact_case = validated_data.get('exact_case', False)

        profile = AppProfile.objects.create(
            provisioning_config=config,
            name=name,
            type=type,
            is_primary=is_primary,
            is_required=is_required,
            multi_value=multi_value,
            exact_case=exact_case,
        )
        return profile


class AppProvisioningSerializer(BaseDynamicFieldModelSerializer):
    class Meta:
        model = Config

        fields = (
            'uuid',
            'base_url',
            'token',
            # 'mode',
            'status',
            'username',
            'password',
            'sync_type',
            'auth_type',
        )


class AddAuthTmplSerializer(serializers.Serializer):

    uuid = serializers.CharField(write_only=True)
    html = serializers.CharField(write_only=True)
    error = serializers.CharField(read_only=True)
    message = serializers.CharField(read_only=True)


class AppNewListSerializer(BaseDynamicFieldModelSerializer):

    class Meta:
        model = App

        fields = (
            'uuid',
            'name',
        )
