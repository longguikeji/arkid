from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
from common.serializer import BaseDynamicFieldModelSerializer
from log.models import Log


class LogSerializer(serializers.Serializer):

    uuid = serializers.CharField(
        read_only=True,
        label=_("唯一标识符")
    )
    timestamp = serializers.DateTimeField(
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

    def to_representation(self, log):
        data = super().to_representation(log)
        data['uuid'] = log.uuid
        data['timestamp'] = log.created.strftime("%Y-%m-%d %H:%M:%S")
        data['user'] = log.data['user']['username']
        data['ip'] = log.data['ip_address']
        data['action'] = log.data['request']['full_path']
        return data


class LogDetailSerializer(BaseDynamicFieldModelSerializer):
    class Meta:
        model = Log

        fields = (
            'uuid',
            'data',
            'created',
        )