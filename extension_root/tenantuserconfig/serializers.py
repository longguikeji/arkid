from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import BaseDynamicFieldModelSerializer
from extension_root.tenantuserconfig.models import TenantUserConfig
from api.v1.fields.custom import create_custom_list_field
from tenant.models import Tenant


# class TenantUserConfigSetSerializer(serializers.Serializer):
#     is_edit_fields = create_custom_list_field(serializers.ListField)(
#         child=serializers.CharField(),
#         label=_("用户编辑字段设置"),
#         url='/api/v1/tenant/{tenant_uuid}/userfields',
#     )
#     is_logout = serializers.BooleanField(label=_("是否允许用户注销自己的账号"))
#     is_look_token = serializers.BooleanField(label=_("设置是否允许用户查看自己当前Token"))
#     is_manual_overdue_token = serializers.BooleanField(label=_("设置是否允许用户手动让Token重置"))
#     is_logging_ip = serializers.BooleanField(label=_("设置是否记录用户的IP地址"))
#     is_logging_device = serializers.BooleanField(label=_("设置是否记录用户的设备信息"))


# class TenantUserConfigSerializer(BaseDynamicFieldModelSerializer):
#     data = TenantUserConfigSetSerializer(
#         label=_("设置")
#     )

#     class Meta:
#         model = TenantUserConfig

#         fields = (
#             'data',
#         )


class TenantUserLogOutConfigSerializer(serializers.Serializer):

    is_logout = serializers.BooleanField(label=_("是否允许用户注销自己的账号"))


class TenantUserTokenConfigSerializer(serializers.Serializer):

    is_look_token = serializers.BooleanField(label=_("设置是否允许用户查看自己当前Token"))
    is_manual_overdue_token = serializers.BooleanField(label=_("设置是否允许用户手动让Token重置"))


class TenantUserLoggingConfigSerializer(serializers.Serializer):

    is_logging_ip = serializers.BooleanField(label=_("设置是否记录用户的IP地址"), required=False)
    is_logging_device = serializers.BooleanField(label=_("设置是否记录用户的设备信息"), required=False)


class TenantUserEditFieldItemConfigSerializer(serializers.Serializer):

    name = serializers.CharField(label=_('中文字段'))
    en_name = serializers.CharField(label=_('英文字段'))
    type = serializers.CharField(label=_('字段类型'))


class TenantUserEditFieldListConfigSerializer(serializers.Serializer):

    results = serializers.ListField(
        child=TenantUserEditFieldItemConfigSerializer(), label=_('字段列表')
    )


class TenantUserConfigFieldSelectItemSerializer(TenantUserEditFieldItemConfigSerializer):
    is_select = serializers.BooleanField(label=_("是否选中"))


class TenantUserConfigFieldSelectListSerializer(serializers.Serializer):

    results = serializers.ListField(
        child=TenantUserConfigFieldSelectItemSerializer(), label=_('字段列表')
    )
