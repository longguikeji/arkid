from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _

class ChoiceSerializer(serializers.Serializer):

    name = serializers.CharField(
        label=_("显示名称")
    )

    value = serializers.CharField(
        label=_("实际值")
    )
