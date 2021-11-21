from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import DataSyncBaseSerializer, ScimServerBaseSerializer

from api.v1.fields.custom import create_foreign_key_field
from api.v1.pages import data_sync
from data_sync.models import DataSyncConfig


class AdDataSyncConfigSerializer(ScimServerBaseSerializer):

    host = serializers.CharField()
    port = serializers.IntegerField()
    bind_dn = serializers.CharField()
    bind_password = serializers.CharField()
    root_dn = serializers.CharField()
    use_tls = serializers.BooleanField(default=False)


class AdDataSyncSerializer(DataSyncBaseSerializer):

    name = serializers.CharField(label=_('配置名称'))
    # sync_mode = serializers.ChoiceField(choices=['server', 'client'], label=_('同步模式'))
    name = serializers.CharField(label=_('同步模式'), default='server', read_only=True)
    data = AdDataSyncConfigSerializer(label=_('data'))


class DataSyncClientConfigSerializer(serializers.Serializer):

    crontab = serializers.CharField(default='0 1 * * *', label=_('定时运行时间'))
    max_retries = serializers.IntegerField(default=3, label=_('重试次数'))
    retry_delay = serializers.IntegerField(default=60, label=_('重试间隔(单位秒)'))

    scim_server = DataSyncBaseSerializer(read_only=True, many=False)
    scim_server_uuid = create_foreign_key_field(serializers.CharField)(
        model_cls=DataSyncConfig,
        field_name='uuid',
        page=data_sync.data_sync_table_tag,
        label=_('同步上游服务端'),
        source="scim_server.uuid",
    )


class ADDataSyncClientConfigSerializer(DataSyncClientConfigSerializer, AdDataSyncConfigSerializer):
    pass


class AdDataSyncClientSerializer(DataSyncBaseSerializer):

    name = serializers.CharField(label=_('配置名称'))
    # sync_mode = serializers.ChoiceField(choices=['server', 'client'], label=_('同步模式'), default='client')
    name = serializers.CharField(label=_('同步模式'), default='client', read_only=True)
    data = ADDataSyncClientConfigSerializer(label=_('data'))
