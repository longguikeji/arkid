from os import read
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

    idp_metadata = serializers.CharField(
        read_only=True,
        label=_("IDP元数据文件"),
    )

class SAMLasIDPSerializer(AppBaseSerializer):

    data = SAMLasIDPConfigSerializer(label=_('data'))

    url = serializers.CharField(
        required = False
    )