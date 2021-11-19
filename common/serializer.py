from lib.dynamic_fields_model_serializer import DynamicFieldsModelSerializer
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _


class BaseDynamicFieldModelSerializer(DynamicFieldsModelSerializer):

    uuid = serializers.UUIDField(label='UUID', read_only=True, format='hex')


class AppBaseSerializer(serializers.Serializer):

    type = serializers.CharField()
    data = serializers.JSONField()

    uuid = serializers.UUIDField(read_only=True)
    name = serializers.CharField()
    url = serializers.URLField()
    description = serializers.CharField()


class AuthRuleBaseSerializer(serializers.Serializer):

    title = serializers.CharField(label=_("标题"))

    type = serializers.CharField(label=_("类型"))

    data = serializers.JSONField(label=_("配置数据"))

    uuid = serializers.UUIDField(read_only=True)

    is_apply = serializers.BooleanField(label=_("是否启用"))


class ExternalIdpBaseSerializer(serializers.Serializer):
    # order_no = serializers.IntegerField()
    type = serializers.CharField()
    data = serializers.JSONField()
    uuid = serializers.UUIDField(read_only=True)


class AuthorizationAgentBaseSerializer(serializers.Serializer):
    # order_no = serializers.IntegerField()
    type = serializers.CharField()
    data = serializers.JSONField()
    uuid = serializers.UUIDField(read_only=True)


class ExtensionBaseSerializer(serializers.Serializer):
    type = serializers.CharField()
    data = serializers.JSONField()
    uuid = serializers.UUIDField(read_only=True)
    is_active = serializers.BooleanField(label=_('是否启用'))


class LoginRegisterConfigBaseSerializer(serializers.Serializer):
    type = serializers.CharField(label=_('登录注册类型'))
    data = serializers.JSONField()
    uuid = serializers.UUIDField(read_only=True)


class OtherAuthFactorBaseSerializer(serializers.Serializer):
    type = serializers.CharField(label=_('认证类型'))
    data = serializers.JSONField()
    uuid = serializers.UUIDField(read_only=True)


class DataSyncBaseSerializer(serializers.Serializer):
    name = serializers.CharField(label=_(''))
    type = serializers.CharField(label=_('同步类型'))
    data = serializers.JSONField()
    uuid = serializers.UUIDField(read_only=True)


class ScimServerBaseSerializer(serializers.Serializer):
    user_url = serializers.URLField(read_only=True)
    group_url = serializers.URLField(read_only=True)
