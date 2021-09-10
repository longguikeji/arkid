from lib.dynamic_fields_model_serializer import DynamicFieldsModelSerializer
from django.contrib.contenttypes.models import ContentType
from inventory.models import Permission
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from api.v1.fields.custom import create_foreign_key_field
from ..pages import app

from app.models import App

class PermissionSerializer(DynamicFieldsModelSerializer):

    uuid = serializers.CharField(read_only=True)
    codename = serializers.CharField(read_only=True)
    is_system_permission = serializers.BooleanField(read_only=True, label=_('是否是系统权限'))
    app_name = serializers.CharField(read_only=True, source='app.name', label=_('应用名称'))
    permission_type = serializers.CharField(read_only=True, source='get_permission_type_display', label=_('权限类型'))

    class Meta:
        model = Permission

        fields = (
            'uuid',
            'name',
            'codename',
            'is_system_permission',
            'app_name',
            'permission_type'
        )


class PermissionCreateSerializer(DynamicFieldsModelSerializer):
    app_uuid = create_foreign_key_field(serializers.CharField)(
        model_cls=App,
        field_name='uuid',
        page=app.tag,
        label=_('应用'),
    )

    class Meta:
        model = Permission

        fields = (
            'uuid',
            'name',
            'codename',
            'app_uuid',
            'permission_type',
        )
    
    def create(self, validated_data):
        tenant = self.context['tenant']
        name = validated_data.get('name', '')
        codename = validated_data.get('codename', '')
        app_uuid = validated_data.get('app_uuid', '')
        permission_type = validated_data.get('permission_type', '')
        content_type = ContentType.objects.get_for_model(App)
        app = App.active_objects.filter(uuid=app_uuid).first()
        app = Permission.objects.create(
            name=name,
            content_type=content_type,
            codename=codename,
            tenant=tenant,
            app=app,
            permission_type=permission_type,
            is_system_permission=False
        )
        return app
