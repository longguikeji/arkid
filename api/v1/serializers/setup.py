from rest_framework import serializers
from django.utils.translation import gettext_lazy as _


class FrontendUrlSerializer(serializers.Serializer):

    url = serializers.CharField(read_only=True, label=_('前端地址'))
