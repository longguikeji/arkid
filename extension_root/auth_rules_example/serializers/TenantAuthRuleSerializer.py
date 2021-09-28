"""
TenantAuthRuleSerializer
"""
from django.utils.translation import ugettext_lazy as _
from auth_rules.serializers import  BaseTenantAuthRuleSerializer
from .TenantAuthRuleDataSerializer import TenantAuthRuleDataSerializer

class TenantAuthRuleSerializer(BaseTenantAuthRuleSerializer):

    data = TenantAuthRuleDataSerializer(
        label=_("规则")
    )
