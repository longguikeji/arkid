from rest_framework import serializers
from common.serializer import BaseDynamicFieldModelSerializer
from django.utils.translation import gettext_lazy as _
from device.models import (
    Device,
)


class DeviceSerializer(BaseDynamicFieldModelSerializer):

    ip = serializers.CharField(label=_('ip'), read_only=True)
    account_ids = serializers.ListField(child=serializers.CharField(), label=_('用户账号ID'), default=[])

    class Meta:
        model = Device

        fields = (
            'uuid',
            'device_type',
            'system_version',
            'browser_version',
            'ip',
            'mac_address',
            'device_number',
            'device_id',
            'account_ids'
        )

    def create(self, validated_data):
        device_id = validated_data.get('device_id')
        account_ids = validated_data.get('account_ids')
        request = self.context['request']
        ip = self.get_client_ip(request)
        validated_data['ip'] = ip
        # 检查device
        device = Device.active_objects.filter(
            device_id=device_id
        ).first()
        if device:
            temp_account_ids = device.account_ids
            for account_id in account_ids:
                if account_id not in temp_account_ids:
                    temp_account_ids.append(account_id)
            device.account_ids = temp_account_ids
            device.save()
        else:
            device = Device.objects.create(
                **validated_data
            )
        return device

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
