from rest_framework import serializers
from rest_framework.fields import HiddenField
from auth_rules.models import TenantAuthRule
from auth_rules.serializers.BaseTenantAuthRuleSerializer import BaseTenantAuthRuleSerializer

class TenantAuthRuleListSerializer(BaseTenantAuthRuleSerializer):
    class Meta:
        model = TenantAuthRule

        fields = (
            "title",
            "data",
            "is_apply",
        )
