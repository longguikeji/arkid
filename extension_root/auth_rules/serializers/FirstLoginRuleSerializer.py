
from common.serializer import AuthRuleBaseSerializer
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from api.v1.fields.custom import create_dynamic_choice_field


class FirstLoginRuleDataSerializer(serializers.Serializer):

    major_auth = create_dynamic_choice_field(serializers.MultipleChoiceField)(
        label=_("主要认证因素"),
        url="",
        form_params=[]
    )

    times = serializers.IntegerField(
        label=_("次数")
    )

    second_auth = create_dynamic_choice_field(serializers.MultipleChoiceField)(
        label=_("主要认证因素"),
        url="",
        form_params=[]
    )

    apps = create_dynamic_choice_field(serializers.MultipleChoiceField)(
        label=_("应用"),
        url="",
        form_params=[]
    )


class FirstLoginRuleSerializer(AuthRuleBaseSerializer):

    data = FirstLoginRuleDataSerializer(
        label=_("认证因素配置")
    )
