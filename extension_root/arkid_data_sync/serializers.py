from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import DataSyncBaseSerializer


class ArkidDataSyncConfigSerializer(serializers.Serializer):

    user_url = serializers.URLField(read_only=True)
    group_url = serializers.URLField(read_only=True)


class ArkidDataSyncSerializer(DataSyncBaseSerializer):

    name = serializers.CharField(label=_('配置名称'))
    sync_mode = serializers.ChoiceField(choices=['server', 'client'], label=_('同步模式'))
    data = ArkidDataSyncConfigSerializer(label=_('data'))