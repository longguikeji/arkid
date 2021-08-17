from common.serializer import BaseDynamicFieldModelSerializer
from login_register_config.models import LoginRegisterConfig
from common.provider import LoginRegisterConfigProvider
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _


class LoginRegisterConfigSerializer(BaseDynamicFieldModelSerializer):
    class Meta:

        model = LoginRegisterConfig

        fields = (
            'uuid',
            'type',
            'data',
        )

    def create(self, validated_data):
        from runtime import get_app_runtime, Runtime

        tenant = self.context['tenant']

        config_type = validated_data.pop('type')
        data = validated_data.pop('data', None)

        config, _ = LoginRegisterConfig.objects.get_or_create(
            tenant=tenant,
            type=config_type,
        )

        if config.is_del:
            config.is_del = False
            config.save()

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

        config_type = validated_data.pop('type')
        data = validated_data.pop('data', None)

        tenant = self.context['tenant']
        r = get_app_runtime()

        provider_cls: LoginRegisterConfigProvider = (
            r.login_register_config_providers.get(config_type, None)
        )
        assert provider_cls is not None
        provider = provider_cls()
        print(data)
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

    class Meta:
        model = LoginRegisterConfig

        fields = ('type',)
