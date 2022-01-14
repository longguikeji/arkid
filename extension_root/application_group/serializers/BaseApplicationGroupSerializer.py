"""
BaseApplicationGroupSerializer
"""
from api.v1.fields.custom import create_foreign_key_field
from app.models import App
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from common.serializer import BaseDynamicFieldModelSerializer
from ..models import ApplicationGroup
from api.v1.pages import app as app_page
from api.v1.pages import user as user_page
from inventory.models import User


class BaseApplicationGroupSerializer(BaseDynamicFieldModelSerializer):
    
    apps = serializers.SerializerMethodField(
        label=_("应用列表")
    )
    
    def get_apps(self,obj):
        apps = obj.apps.filter(is_active=True,is_del=False).all()
        return [{
            "name": app.name,
            "uuid": app.uuid,
        } for app in apps]
    
    
    class Meta:
        model = ApplicationGroup
        fields = [
            "uuid",
            "id",
            "name",
            "apps",
        ]

        extra_kwargs = {
            'uuid': {'read_only': True},
        }
