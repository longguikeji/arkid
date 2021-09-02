
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
        label=_("次数")
    )

    second_auth = create_multiple_dynamic_choice_field(serializers.MultipleChoiceField)(
        label=_("主要认证因素"),
        url=f'/api/v1/auth_rule/auth_factor_choices_list/?{"tenant={tenant_uuid}"}&{"exclude={major_auth}"}'
    )

    apps = create_multiple_dynamic_choice_field(serializers.MultipleChoiceField)(
        label=_("应用"),
         url=f'/api/v1/auth_rule/app_choices_list/?{"tenant={tenant_uuid}"}'
    )


class FirstLoginRuleSerializer(AuthRuleBaseSerializer):

    data = FirstLoginRuleDataSerializer(
        label=_("认证因素配置")
    )
