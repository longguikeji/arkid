"""
BaseApplicationMultipleIpSerializer
"""
from api.v1.fields.custom import create_foreign_key_field
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from common.serializer import BaseDynamicFieldModelSerializer
from ..models import ApplicationMultipleIp
from app.models import App
from api.v1.pages import app as app_page


class BaseApplicationMultipleIpSerializer(BaseDynamicFieldModelSerializer):

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

    class Meta:
        model = ApplicationMultipleIp
        fields = [
            "id",
            "ip_regx",
            "ip",
            "app",
            "app_name",
            "uuid"
        ]

        extra_kwargs = {
            'uuid': {'read_only': True},
        }
