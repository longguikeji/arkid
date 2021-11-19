from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import DataSyncBaseSerializer, ScimServerBaseSerializer


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
    sync_mode = serializers.ChoiceField(choices=['server', 'client'], label=_('同步模式'))
    data = MssqlDataSyncConfigSerializer(label=_('data'))
