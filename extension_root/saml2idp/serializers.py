from os import read
from django.db.models import fields
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import AppBaseSerializer
from django.conf import settings
from api.v1.fields.custom import create_dowload_url_field

class SAMLasIDPConfigSerializer(serializers.Serializer):
    
    entity_id = serializers.CharField(
        required=False
    )

    acs = serializers.URLField(
        required=False
    )

    sls = serializers.URLField(
        required=False
    )

    cert = serializers.CharField(
        label=_("证书公钥"),
        required=False
    )

    xmldata = serializers.CharField(
        label=_("元数据文件")
    )

    idp_metadata = create_dowload_url_field(serializers.CharField)(
        hint=_("点击下载"),
        label=_("IDP元数据文件"),
        read_only=True
    )

    sso_url = serializers.CharField(
        label=_("登陆地址"),
    )

class SAMLasIDPSerializer(AppBaseSerializer):

    data = SAMLasIDPConfigSerializer(label=_('data'))

    url = serializers.CharField(
        required = False
    )