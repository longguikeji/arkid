from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import ExternalIdpBaseSerializer


class SAML2SPConfigSerializer(serializers.Serializer):
    
    idp_name = serializers.CharField(
        label=_("身份提供商名称")
    )

    remarks = serializers.CharField(
        label=_("备注")
    )

    metadata = serializers.CharField(
        label=_("元数据文档")
    )

class SAML2SPSerializer(ExternalIdpBaseSerializer):

    data = SAML2SPConfigSerializer(label=_('数据'))