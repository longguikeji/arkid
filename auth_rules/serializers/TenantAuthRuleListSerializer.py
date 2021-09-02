from auth_rules.models import TenantAuthRule
from auth_rules.serializers.BaseTenantAuthRuleSerializer import BaseTenantAuthRuleSerializer

class TenantAuthRuleListSerializer(BaseTenantAuthRuleSerializer):
    class Meta:
        model = TenantAuthRule

        fields = (
            "id",
            "is_apply",
            "title",
            "data"
        )
