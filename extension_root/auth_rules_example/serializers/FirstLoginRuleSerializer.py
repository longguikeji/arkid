
from config import get_app_config
from common.serializer import AuthRuleBaseSerializer
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from api.v1.fields.custom import create_multiple_dynamic_choice_field


class FirstLoginRuleDataSerializer(serializers.Serializer):

    major_auth = create_multiple_dynamic_choice_field(serializers.MultipleChoiceField)(
        label=_("主要认证因素"),
        url=f'/api/v1/auth_rule/auth_factor_choices_list/?{"tenant={tenant_uuid}"}'
    )

    times = serializers.IntegerField(
        label=_("失败次数")
    )

    second_auth = create_multiple_dynamic_choice_field(serializers.MultipleChoiceField)(
        label=_("次要认证因素"),
        url=f'/api/v1/auth_rule/auth_factor_choices_list/?{"tenant={tenant_uuid}"}&{"exclude={major_auth}"}',
        required=False
    )
class FirstLoginRuleSerializer(AuthRuleBaseSerializer):

    data = FirstLoginRuleDataSerializer(
        label=_("认证因素配置")
    )
