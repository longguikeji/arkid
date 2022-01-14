"""
BaseMessageSerializer
"""
from api.v1.fields.custom import create_foreign_key_field
from app.models import App
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from common.serializer import BaseDynamicFieldModelSerializer
from ..models import Message
from api.v1.pages import app as app_page


class MessageSerializer(BaseDynamicFieldModelSerializer):

    app_name = serializers.SerializerMethodField(
        label=_("应用名称")
    )

    def get_app_name(self, obj):
        return obj.app.name

    class Meta:
        model = Message
        fields = [
            "id",
            "title",
            "time",
            "content",
            "app_name",
            "uuid",
            "users",
            "url",
            "type"
        ]

        extra_kwargs = {
            'uuid': {'read_only': True},
            "app_name": {'read_only': True}
        }
