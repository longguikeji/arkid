from common.serializer import BaseDynamicFieldModelSerializer
from authorization_agent.models import AuthorizationAgent
from common.provider import AuthorizationAgentProvider
from rest_framework import serializers
from django.db.models import Max


class AuthorizationAgentSerializer(BaseDynamicFieldModelSerializer):

    class Meta:

        model = AuthorizationAgent

        fields = (
            'uuid',
            'type',
            'data',
            'order_no',
        )

    def create(self, validated_data):
        from runtime import get_app_runtime, Runtime

        tenant = self.context['tenant']

        authorization_agent_type = validated_data.pop('type')
        data = validated_data.pop('data', None)

        authorization_agent, _ = AuthorizationAgent.objects.get_or_create(
            tenant=tenant,
            type=authorization_agent_type,
        )
        authorization_agent.is_del = False
        authorization_agent.is_active = True

        if not authorization_agent.order_no:
            max_order_no = (
                AuthorizationAgent.objects.filter(tenant=tenant)
                .aggregate(Max('order_no'))
                .get('order_no__max')
            )
            authorization_agent.order_no = max_order_no + 1

        if authorization_agent.is_del:
            authorization_agent.is_del = False
            authorization_agent.save()

        r: Runtime = get_app_runtime()
        provider_cls: AuthorizationAgentProvider = r.authorization_agent_providers.get(
            authorization_agent_type, None
        )
        assert provider_cls is not None

        provider = provider_cls()
        data = provider.create(tenant_uuid=tenant.uuid, authorization_agent=authorization_agent, data=data)
        if data is not None:
            authorization_agent.data = data
        authorization_agent.save()

        return authorization_agent

    def update(self, instance, validated_data):
        from runtime import get_app_runtime
        authorization_agent_type = validated_data.pop('type')
        data = validated_data.pop('data', None)

        tenant = self.context['tenant']
        r = get_app_runtime()

        provider_cls: AuthorizationAgentProvider = r.authorization_agent_providers.get(
            authorization_agent_type, None
        )
        assert provider_cls is not None
        provider = provider_cls()
        print(data)
        data = provider.create(tenant_uuid=tenant.uuid, authorization_agent=instance, data=data)
        print('----设置递增信息----')
        print(data)
        if data is not None:
            instance.data = data
        instance.type = authorization_agent_type
        instance.save()
        return instance


class AuthorizationAgentListSerializer(AuthorizationAgentSerializer):
    class Meta:
        model = AuthorizationAgent

        fields = (
            'type',
            'order_no',
        )


class AuthorizationAgentReorderSerializer(serializers.Serializer):

    idps = serializers.ListField(child=serializers.CharField(), write_only=True)

    error = serializers.CharField(read_only=True)
