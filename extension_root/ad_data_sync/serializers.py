from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import DataSyncBaseSerializer, ScimServerBaseSerializer


class AdDataSyncConfigSerializer(ScimServerBaseSerializer):

    host = serializers.CharField()
    port = serializers.IntegerField()
    bind_dn = serializers.CharField()
    bind_password = serializers.CharField()
    root_dn = serializers.CharField()
    use_tls = serializers.BooleanField(default=False)


class AdDataSyncSerializer(DataSyncBaseSerializer):

    name = serializers.CharField(label=_('配置名称'))
    sync_mode = serializers.ChoiceField(choices=['server', 'client'], label=_('同步模式'))
    data = AdDataSyncConfigSerializer(label=_('data'))
