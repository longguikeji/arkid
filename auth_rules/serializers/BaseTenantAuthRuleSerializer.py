"""
BaseTenantAuthRuleSerializer
"""
from common.provider import BaseAuthRuleProvider
from runtime import get_app_runtime
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from common.serializer import BaseDynamicFieldModelSerializer
from auth_rules.models import TenantAuthRule

class BaseTenantAuthRuleSerializer(BaseDynamicFieldModelSerializer):

    class Meta:
        model = TenantAuthRule
        fields = [
            "type",
            "id",
            "title",
            "data",
            "is_apply",
        ]

    @transaction.atomic()
    def create(self, validated_data):
        print(validated_data)
        tenant = self.context['tenant']

        auth_rule = TenantAuthRule.objects.create(
            tenant=tenant,
            **validated_data
        )

        _type = validated_data.pop('type')

        r = get_app_runtime()
        provider_cls: BaseAuthRuleProvider = r.auth_rule_type_providers.get(_type, None)
        assert provider_cls is not None
        provider = provider_cls()
        data = provider.create(
            auth_rule=auth_rule, 
            data=validated_data.get("data",{})
        )
        if data is not None:
            auth_rule.data = data
            auth_rule.save()
        # transaction.on_commit(
        #     lambda: WebhookManager.app_created(self.context['tenant'].uuid, app)
        # )
        return auth_rule


