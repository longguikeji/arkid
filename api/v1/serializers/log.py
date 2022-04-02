from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
from common.serializer import BaseDynamicFieldModelSerializer
from log.models import Log
from requestlogs.storages import BaseEntrySerializer


class LogSerializer(serializers.Serializer):

    created = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M:%S",
        read_only=True,
        label=_("时间")
    )
    user = serializers.CharField(
        read_only=True,
        label=_("用户")
    )
    ip = serializers.CharField(
        read_only=True,
        label=_("ip地址")
    )
    action = serializers.CharField(
        read_only=True,
        label=_("操作")
    )
    status_code = serializers.IntegerField(
        read_only=True,
        label=_("状态码")
    )

    def to_representation(self, log):
        data = super().to_representation(log)
        data['uuid'] = log.uuid
        data['user'] = log.data['user'].get('username', '')
        data['ip'] = log.data['ip_address']
        data['action'] = log.data['request'].get('path', '')
        data['status_code'] = log.data['response'].get('status_code', '')
        return data


class CustomBaseEntrySerializer(BaseEntrySerializer):
    execution_time = serializers.CharField(read_only=True)


class CustomEntrySerializer(CustomBaseEntrySerializer):
    class TenantLogSerializer(serializers.Serializer):
        uuid = serializers.CharField(read_only=True)
        name = serializers.CharField(read_only=True)
        slug = serializers.CharField(read_only=True)

    class UserLogSerializer(serializers.Serializer):
        uuid = serializers.CharField(read_only=True)
        username = serializers.CharField(read_only=True)
        admin = serializers.BooleanField(read_only=True)

    tenant = TenantLogSerializer()
    user = UserLogSerializer()
    host = serializers.CharField(read_only=True)


class LogDetailSerializer(BaseDynamicFieldModelSerializer):

    data = CustomEntrySerializer(label=_('data'))

    class Meta:
        model = Log

        fields = (
            'uuid',
            'data',
            'created',
        )
