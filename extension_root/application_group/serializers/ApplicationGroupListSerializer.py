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


class ApplicationGroupListSerializer(BaseDynamicFieldModelSerializer):
    
    class Meta:
        model = ApplicationGroup
        fields = [
            "uuid",
            "id",
            "name",
        ]

        extra_kwargs = {
            'uuid': {'read_only': True},
        }
