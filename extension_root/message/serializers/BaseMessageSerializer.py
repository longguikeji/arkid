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
from api.v1.pages import user as user_page
from inventory.models import User


class BaseMessageSerializer(BaseDynamicFieldModelSerializer):

    app_name = serializers.SerializerMethodField(
        label=_("应用名称")
    )

    def get_app_name(self, obj):
        return obj.app.name

    app = create_foreign_key_field(serializers.CharField)(
        model_cls=App,
        field_name='uuid',
        page=app_page.app_only_list_tag,
        label=_('应用'),
        source="app.uuid",
    )

    users = create_foreign_key_field(serializers.ListField)(
        model_cls=User,
        field_name='uuid',
        page=user_page.user_table_tag,
        child=serializers.CharField(),
        default=[],
        label=_('用户'),
        source="user.uuid",
        required=False
    )

    class Meta:
        model = Message
        fields = [
            "id",
            "title",
            "time",
            "app",
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
