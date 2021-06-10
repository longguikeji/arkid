from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import ExternalIdpBaseSerializer


class GiteeBindSerializer(serializers.Serializer):

    user_id = serializers.CharField()


class GiteeExternalIdpConfigSerializer(serializers.Serializer):

    client_id = serializers.CharField()
    secret_id = serializers.CharField()

    login_url = serializers.URLField(read_only=True)
    callback_url = serializers.URLField(read_only=True)
    bind_url = serializers.URLField(read_only=True)
    img_url = serializers.URLField(read_only=True)


class GiteeExternalIdpSerializer(ExternalIdpBaseSerializer):

    data = GiteeExternalIdpConfigSerializer(label=_('data'))


class GiteeDataSerializer(serializers.Serializer):

    url = serializers.CharField(label=_('请求地址'))
    method = serializers.CharField(label=_('请求方法 get or post'))
    params = serializers.CharField(label=_('这个参数名称不固定，数量不固定，根据gitee文档来传就可以'), required=False)
