from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import ExternalIdpBaseSerializer


class MiniProgramExternalIdpConfigSerializer(serializers.Serializer):

    app_id = serializers.CharField()
    secret_id = serializers.CharField()

    login_url = serializers.URLField(read_only=True)
    bind_url = serializers.URLField(read_only=True)


class MiniProgramBindSerializer(serializers.Serializer):

    user_id = serializers.CharField()
    name = serializers.CharField()
    avatar = serializers.CharField()


class MiniProgramExternalIdpSerializer(ExternalIdpBaseSerializer):

    data = MiniProgramExternalIdpConfigSerializer(label=_('data'))


class MiniProgramLoginSerializer(serializers.Serializer):

    code = serializers.CharField()
    name = serializers.CharField()
    avatar = serializers.CharField()


class MiniProgramLoginResponseSerializer(serializers.Serializer):

    token = serializers.CharField(label=_('token，只会在已绑定出'))
    user_id = serializers.CharField(label=_('user_id，只会在未绑定出'))
    name = serializers.CharField(label=_('名称，只会在未绑定出'))
    avatar = serializers.CharField(label=_('头像，只会在未绑定出'))
    tenant_uuid = serializers.CharField(label=_('租户uuid，只会在未绑定出'))
    bind = serializers.CharField(label=_('绑定的url，只会在未绑定出'))


class MiniProgramBindResponseSerializer(serializers.Serializer):

    token = serializers.CharField(label=_('token'))
