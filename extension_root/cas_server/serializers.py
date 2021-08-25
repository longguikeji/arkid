from rest_framework import serializers
from oauth2_provider.models import Application
from common.serializer import AppBaseSerializer
from api.v1.fields.custom import create_hint_field


class CasAppConfigSerializer(serializers.Serializer):

    login = serializers.URLField(read_only=True)
    validate = serializers.URLField(read_only=True)


class CasAppSerializer(AppBaseSerializer):
    data = CasAppConfigSerializer(label='数据')
