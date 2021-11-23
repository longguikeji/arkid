from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import DataSyncBaseSerializer, ScimServerBaseSerializer
from api.v1.fields.custom import create_foreign_key_field
from api.v1.pages import data_sync
from data_sync.models import DataSyncConfig


class MssqlDataSyncConfigSerializer(serializers.Serializer):

    server = serializers.CharField()
    port = serializers.IntegerField()
    user = serializers.CharField()
    password = serializers.CharField()
    database = serializers.CharField()
    emp_table = serializers.CharField()
    dept_table = serializers.CharField()
    job_table = serializers.CharField()
    company_table = serializers.CharField()
    user_url = serializers.URLField(read_only=True)
    group_url = serializers.URLField(read_only=True)


class MssqlDataSyncSerializer(DataSyncBaseSerializer):

    name = serializers.CharField(label=_('配置名称'))
    # sync_mode = serializers.ChoiceField(choices=['server', 'client'], label=_('同步模式'))
    sync_mode = serializers.CharField(label=_('同步模式'), default='server', read_only=True)
    data = MssqlDataSyncConfigSerializer(label=_('data'))


class MssqlDataSyncClientConfigSerializer(serializers.Serializer):

    server = serializers.CharField()
    port = serializers.IntegerField()
    user = serializers.CharField()
    password = serializers.CharField()
    database = serializers.CharField()
    emp_table = serializers.CharField()
    dept_table = serializers.CharField()


class DataSyncClientConfigSerializer(serializers.Serializer):

    crontab = serializers.CharField(default='0 1 * * *', label=_('定时运行时间'))
    max_retries = serializers.IntegerField(default=3, label=_('重试次数'))
    retry_delay = serializers.IntegerField(default=60, label=_('重试间隔(单位秒)'))

    # scim_server = DataSyncBaseSerializer(同步上游服务端 many=False)
    scim_server_name = serializers.CharField(label=_('同步上游服务端'), read_only=True)
    scim_server_uuid = create_foreign_key_field(serializers.CharField)(
        model_cls=DataSyncConfig,
        field_name='uuid',
        page=data_sync.data_sync_table_tag,
        label=_('同步上游服务端'),
        link='scim_server_name',
    )


class MssqlDataSyncClientConfigSerializer(DataSyncClientConfigSerializer, MssqlDataSyncClientConfigSerializer):
    pass


class MssqlDataSyncClientSerializer(DataSyncBaseSerializer):

    name = serializers.CharField(label=_('配置名称'))
    # sync_mode = serializers.ChoiceField(choices=['server', 'client'], label=_('同步模式'), default='client')
    sync_mode = serializers.CharField(label=_('同步模式'), default='client', read_only=True)
    data = MssqlDataSyncClientConfigSerializer(label=_('data'))
