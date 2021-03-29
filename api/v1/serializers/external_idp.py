from common.serializer import BaseDynamicFieldModelSerializer
from external_idp.models import ExternalIdp
from common.provider import ExternalIdpProvider

class ExternalIdpSerializer(BaseDynamicFieldModelSerializer):

    class Meta:

        model = ExternalIdp

        fields = (
            'uuid',
            'type',
            'data',
        )

    def create(self, validated_data):
        from runtime import get_app_runtime, Runtime
        tenant = self.context['tenant']

        external_idp_type = validated_data.pop('type')
        data = validated_data.pop('data', None)

        external_idp, _ = ExternalIdp.objects.get_or_create(
            tenant=tenant,
            type=external_idp_type,
        )

        r: Runtime = get_app_runtime()
        provider_cls: ExternalIdpProvider = r.external_idp_providers.get(external_idp_type, None)
        assert provider_cls is not None

        provider = provider_cls()
        data = provider.create(tenant_id=tenant.id, external_idp=external_idp, data=data)
        if data is not None:
            external_idp.data = data
            external_idp.save()

        return external_idp

    
class ExternalIdpListSerializer(ExternalIdpSerializer):

    class Meta:
        model = ExternalIdp

        fields = (
            'type',
        )