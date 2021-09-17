from common.serializer import BaseDynamicFieldModelSerializer
from login_register_config.models import LoginRegisterConfig
from common.provider import LoginRegisterConfigProvider
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from tenant.models import Tenant


class LoginRegisterConfigSerializer(BaseDynamicFieldModelSerializer):
    login_enabled = serializers.SerializerMethodField(label=_('启用登录'))
    register_enabled = serializers.SerializerMethodField(label=_('启用注册'))
    reset_password_enabled = serializers.SerializerMethodField(label=_('启用重置密码'))
    class Meta:

        model = LoginRegisterConfig

        fields = (
            'uuid',
            'type',
            'data',
            'login_enabled',
            'register_enabled',
            'reset_password_enabled',
        )

    def get_login_enabled(self, instance):
        return instance.data.get('login_enabled')

    def get_register_enabled(self, instance):
        return instance.data.get('register_enabled')

    def get_reset_password_enabled(self, instance):
        return instance.data.get('reset_password_enabled')

    def create(self, validated_data):
        from runtime import get_app_runtime, Runtime

        request = self.context['request']
        tenant_uuid = request.query_params.get('tenant')
        if not tenant_uuid:
            tenant = None
        else:
            tenant = Tenant.valid_objects.filter(uuid=tenant_uuid).first()

        config_type = validated_data.pop('type')
        data = validated_data.pop('data', None)

        config = LoginRegisterConfig.valid_objects.create(
            tenant=tenant,
            type=config_type,
        )

        r: Runtime = get_app_runtime()
        provider_cls: LoginRegisterConfigProvider = (
            r.login_register_config_providers.get(config_type, None)
        )
        assert provider_cls is not None

        # provider = provider_cls()
        # data = provider.create(
        #     tenant_uuid=tenant.uuid, external_idp=external_idp, data=data
        # )
        # if data is not None:
        #     external_idp.data = data
        config.data = data
        config.save()

        return config

    def update(self, instance, validated_data):
        from runtime import get_app_runtime

        request = self.context['request']
        tenant_uuid = request.query_params.get('tenant')
        if not tenant_uuid:
            tenant = None
        else:
            tenant = Tenant.valid_objects.filter(uuid=tenant_uuid).first()

        config_type = validated_data.pop('type')
        data = validated_data.pop('data', None)

        r = get_app_runtime()

        provider_cls: LoginRegisterConfigProvider = (
            r.login_register_config_providers.get(config_type, None)
        )
        assert provider_cls is not None
        # provider = provider_cls()
        # data = provider.create(
        #     tenant_uuid=tenant.uuid, external_idp=instance, data=data
        # )
        # print('----设置递增信息----')
        # print(data)
        # if data is not None:
        #     instance.data = data
        instance.type = config_type
        instance.data = data
        instance.save()
        return instance


class LoginRegisterConfigListSerializer(LoginRegisterConfigSerializer):
    type = serializers.CharField(label=_('登录注册类型'))
    login_enabled = serializers.BooleanField(label=_('启用登录'))
    register_enabled = serializers.BooleanField(label=_('启用注册'))
    reset_password_enabled = serializers.BooleanField(label=_('启用重置密码'))

    class Meta:
        model = LoginRegisterConfig

        fields = ('type', 'login_enabled', 'register_enabled', 'reset_password_enabled')