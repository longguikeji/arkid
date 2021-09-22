from common.serializer import BaseDynamicFieldModelSerializer
from login_register_config.models import OtherAuthFactor
from common.provider import OtherAuthFactorProvider
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from tenant.models import Tenant


class OtherAuthFactorSerializer(BaseDynamicFieldModelSerializer):
    class Meta:

        model = OtherAuthFactor

        fields = (
            'uuid',
            'type',
            'data',
        )

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

        config = OtherAuthFactor.valid_objects.create(
            tenant=tenant,
            type=config_type,
        )

        r: Runtime = get_app_runtime()
        provider_cls: OtherAuthFactorProvider = r.other_auth_factor_providers.get(
            config_type, None
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

        provider_cls: OtherAuthFactorProvider = r.other_auth_factor_providers.get(
            config_type, None
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


class OtherAuthFactorListSerializer(OtherAuthFactorSerializer):
    type = serializers.CharField(label=_('其他认证因素类型'))

    class Meta:
        model = OtherAuthFactor

        fields = ('type',)
