#!/usr/bin/env python3

from import_export import resources
from tenant.models import TenantDevice


class TenantDeviceResource(resources.ModelResource):

    class Meta:
        model = TenantDevice
        fields = (
            'device_type',
            'system_version',
            'browser_version',
            'ip',
            'mac_address',
            'device_number',
            'device_id',
            'account_ids'
        )
        exclude = (
            'is_active',  # not null
            'uuid',  # not null
            'is_del',  # not null
            'updated',
            'created',
        )
