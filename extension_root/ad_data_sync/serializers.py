from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import DataSyncBaseSerializer, ScimServerBaseSerializer


class AdDataSyncConfigSerializer(ScimServerBaseSerializer):

    host = serializers.CharField()
    password = serializers.CharField()
    bind_dn = serializers.CharField()
    bind_password = serializers.CharField()
    use_tls = serializers.BooleanField(default=False)


class AdDataSyncSerializer(DataSyncBaseSerializer):

    data = AdDataSyncConfigSerializer(label=_('data'))
    name = serializers.CharField(label=_('配置名称'))
