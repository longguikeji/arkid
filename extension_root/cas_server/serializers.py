from rest_framework import serializers
from oauth2_provider.models import Application
from common.serializer import AppBaseSerializer
from django.utils.translation import gettext_lazy as _
from api.v1.fields.custom import create_hint_field, create_upload_url_field


class CasAppConfigSerializer(serializers.Serializer):

    login = serializers.URLField(read_only=True)
    validate = serializers.URLField(read_only=True)


class CasAppSerializer(AppBaseSerializer):
    url = create_hint_field(serializers.URLField)(hint="请填写正确的url格式")
    logo = create_upload_url_field(serializers.URLField)(
        hint=_("请选择图标"), required=False
    )
    data = CasAppConfigSerializer(label='数据')
