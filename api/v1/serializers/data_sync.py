from common.serializer import BaseDynamicFieldModelSerializer
from data_sync.models import DataSyncConfig
from common.provider import DataSyncProvider
from rest_framework import serializers


class DataSyncSerializer(BaseDynamicFieldModelSerializer):
    class Meta:

        model = DataSyncConfig

        fields = (
            'uuid',
            'type',
            'data',
            'name',
            'sync_mode',
        )

    def create(self, validated_data):
        from runtime import get_app_runtime, Runtime

        tenant = self.context['tenant']

        name = validated_data.pop('name', None)
        sync_mode = validated_data.pop('sync_mode', None)
        data_sync_type = validated_data.pop('type')
        data = validated_data.pop('data', None)

        data_sync_config, _ = DataSyncConfig.objects.get_or_create(
            tenant=tenant,
            type=data_sync_type,
            sync_mode=sync_mode,
        )

        r: Runtime = get_app_runtime()
        provider_cls: DataSyncProvider = r.data_sync_providers.get(data_sync_type, None)
        assert provider_cls is not None

        data = provider_cls.create(tenant_uuid=tenant.uuid, data=data)
        if data is not None:
            data_sync_config.data = data
        data_sync_config.name = name
        data_sync_config.save()

        return data_sync_config

    def update(self, instance, validated_data):
        from runtime import get_app_runtime

        data_sync_type = validated_data.pop('type')
        name = validated_data.pop('name', None)
        data = validated_data.pop('data', None)

        tenant = self.context['tenant']
        r = get_app_runtime()

        provider_cls: DataSyncProvider = r.data_sync_providers.get(data_sync_type, None)
        assert provider_cls is not None
        data = provider_cls.update(tenant_uuid=tenant.uuid, data=data)
        if data is not None:
            instance.data = data
        instance.type = data_sync_type
        instance.name = name
        instance.save()
        return instance


class DataSyncListSerializer(DataSyncSerializer):
    class Meta:
        model = DataSyncConfig

        fields = ('name', 'type', 'sync_mode')
