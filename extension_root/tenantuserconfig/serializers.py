from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import BaseDynamicFieldModelSerializer
from extension_root.tenantuserconfig.models import TenantUserConfig
from tenant.models import Tenant


class TenantUserConfigSetSerializer(serializers.Serializer):
    is_edit_fields = serializers.ListField(
        child=serializers.CharField(), label=_('用户编辑字段设置')
    )
    is_logout = serializers.BooleanField(label=_("是否允许用户注销自己的账号"))
    is_look_token = serializers.BooleanField(label=_("设置是否允许用户查看自己当前Token"))
    is_manual_overdue_token = serializers.BooleanField(
        label=_("设置是否允许用户手动让Token重置"))
    is_logging_ip = serializers.BooleanField(label=_("设置是否记录用户的IP地址"))
    is_logging_device = serializers.BooleanField(label=_("设置是否记录用户的设备信息"))


class TenantUserConfigSerializer(BaseDynamicFieldModelSerializer):
    data = TenantUserConfigSetSerializer(
        label=_("设置")
    )

    class Meta:
        model = TenantUserConfig

        fields = (
            'data',
        )


class TenantUserConfigFieldSerializer(serializers.Serializer):

    fields = serializers.ListField(
        child=serializers.CharField(), label=_('字段列表')
    )
