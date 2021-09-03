from rest_framework import serializers
from common.serializer import BaseDynamicFieldModelSerializer
from common.utils import get_client_ip
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
        tenant_uuid = self.context['tenant_uuid']
        ip = ''
        if tenant_uuid:
            from tenant.models import Tenant
            from extension_root.tenantuserconfig.models import TenantUserConfig
            tenant = Tenant.active_objects.get(uuid=tenant_uuid)
            config = TenantUserConfig.active_objects.filter(
                tenant=tenant
            ).first()
            if config:
                data = config.data
                is_logging_ip = data['is_logging_ip']
                if is_logging_ip is True:
                    ip = get_client_ip(request)
        else:
            ip = get_client_ip(request)
        validated_data['ip'] = ip
        # 检查device
        device = Device.active_objects.filter(
            device_id=device_id
        ).first()
        if device and device_id:
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
