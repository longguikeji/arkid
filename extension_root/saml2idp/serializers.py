from django.db.models import fields
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import AppBaseSerializer
from django.conf import settings


class SAMLasIDPConfigSerializer(serializers.Serializer):
    
    entity_id = serializers.CharField(
        required=False
    )

    acs = serializers.URLField(
        label=_("登录接口"),
        required=False
    )

    sls = serializers.URLField(
        label=_("登出接口"),
        required=False
    )

    cert = serializers.CharField(
        label=_("证书公钥"),
    )

    xmldata = serializers.CharField(
        label=_("元数据文件")
    )

    if settings.DEBUG:
        metadata_file_path = serializers.CharField(
            read_only=True,
            label=_("IDP元数据文件路径")
        )

class SAMLasIDPSerializer(AppBaseSerializer):

    data = SAMLasIDPConfigSerializer(label=_('data'))

    url = serializers.CharField(
        read_only=True
    )