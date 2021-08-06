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

    @transaction.atomic()
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
        provisioning = self.context['provisioning']

        mapping_type = validated_data.pop('mapping_type')
        default_value = validated_data.pop('default_value')
        source_attribute = validated_data.pop('source_attribute')
        target_attribute = validated_data.pop('target_attribute')
        is_used_matching = validated_data.pop('is_used_matching')
        constant_value = validated_data.pop('constant_value')
        apply_type = validated_data.pop('apply_type')

        mapping = Schema.objects.create(
            provisioning_config=provisioning,
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
            'name',
            'type',
            'is_primary',
            'is_required',
            'multi_value',
            'exact_case',
        )

    def create(self, validated_data):
        provisioning = self.context['provisioning']

        name = validated_data.pop('name')
        type = validated_data.pop('type')
        is_primary = validated_data.pop('is_primary')
        is_required = validated_data.pop('is_required')
        multi_value = validated_data.pop('multi_value')
        exact_case = validated_data.pop('exact_case')

        profile = AppProfile.objects.create(
            provisioning_config=provisioning,
            name=name,
            type=type,
            is_primary=is_primary,
            is_required=is_required,
            multi_value=multi_value,
            exact_case=exact_case,
        )
        return profile


class AppProvisioningSerializer(BaseDynamicFieldModelSerializer):
    # app_profile_mappings = AppProvisioningMappingSerializer(many=True)
    # app_profile = AppProvisioningProfileSerializer(many=True)

    class Meta:
        model = Config

        fields = (
            'base_url',
            'token',
            # 'app_profile_mappings',
            # 'app_profile',
            # 'mode',
            'status',
            'username',
            'password',
            'sync_type',
            'auth_type',
        )

    def create(self, validated_data):
        app = self.context['app']

        base_url = validated_data.pop('base_url')
        sync_type = validated_data.pop('sync_type')
        auth_type = validated_data.pop('auth_type')
        token = validated_data.pop('token')
        # mode = validated_data.pop('mode', 0)
        status = validated_data.pop('status', 1)
        username = validated_data.pop('username')
        password = validated_data.pop('password')

        app_profile_mappings = validated_data.pop('app_profile_mappings', [])
        app_profile = validated_data.pop('app_profile', [])

        provision = Config.objects.create(
            app=app,
            sync_type=sync_type,
            auth_type=auth_type,
            base_url=base_url,
            token=token,
            status=status,
            username=username,
            password=password,
        )

        # for mp in app_profile_mappings:
        #     obj = Schema.objects.create(
        #         default_value=mp.get('default_value', ''),
        #         source_attribute=mp.get('source_attribute', ''),
        #         target_attribute=mp.get('target_attribute', ''),
        #         is_used_matching=mp.get('is_used_matching', False),
        #         matching_precedence=mp.get('matching_precedence', -1),
        #         constant_value=mp.get('constant_value', ''),
        #         apply_type=mp.get('apply_type', 0),
        #     )
        #     provision.app_profile_mappings.add(obj)
        # for profile in app_profile:
        #     obj = AppProfile.create(
        #         name=profile.get('name', ''),
        #         type=profile.get('type', 0),
        #         is_primary=profile.get('is_primary', False),
        #         is_required=profile.get('is_required', False),
        #         multi_value=profile.get('multi_value', False),
        #         exact_case=profile.get('exact_case', False),
        #     )
        #     provision.app_profile.add(obj)
        # provision.save()

        return provision


class AddAuthTmplSerializer(serializers.Serializer):

    uuid = serializers.CharField(write_only=True)
    html = serializers.CharField(write_only=True)
    error = serializers.CharField(read_only=True)
    message = serializers.CharField(read_only=True)
