from lib.dynamic_fields_model_serializer import DynamicFieldsModelSerializer
from django.contrib.contenttypes.models import ContentType
from inventory.models import Permission, PermissionGroup
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from api.v1.fields.custom import create_foreign_key_field
from ..pages import app, permission
from app.models import App

import uuid


class PermissionSerializer(DynamicFieldsModelSerializer):

    uuid = serializers.CharField(read_only=True)
    codename = serializers.CharField(read_only=True)
    is_system_permission = serializers.BooleanField(
        read_only=True, label=_('是否是系统权限'))
    app_name = serializers.CharField(
        read_only=True, source='app.name', label=_('应用名称'))

    class Meta:
        model = Permission

        fields = (
            'uuid',
            'name',
            'codename',
            'is_system_permission',
            'app_name',
            'permission_category'
        )


class PermissionCreateSerializer(DynamicFieldsModelSerializer):

    uuid = serializers.CharField(read_only=True)
    codename = serializers.CharField(read_only=True)
    permission_category = serializers.ChoiceField(
        choices=['入口', 'API', '数据'], label=_('权限类型'))
    is_system_permission = serializers.BooleanField(
        read_only=True, label=_('是否是系统权限'))
    app_uuid = create_foreign_key_field(serializers.CharField)(
        model_cls=App,
        field_name='uuid',
        page=app.tag,
        label=_('应用'),
        source="app.uuid",
    )

    class Meta:
        model = Permission

        fields = (
            'uuid',
            'name',
            'codename',
            'app_uuid',
            'permission_category',
            'is_system_permission',
        )

    def create(self, validated_data):
        tenant = self.context['tenant']
        name = validated_data.get('name', '')
        app_uuid = validated_data.get('app', '').get('uuid')
        codename = 'custom_{}'.format(uuid.uuid4())
        permission_category = validated_data.get('permission_category', '')
        content_type = ContentType.objects.get_for_model(App)
        app = App.active_objects.filter(uuid=app_uuid).first()
        app = Permission.objects.create(
            name=name,
            content_type=content_type,
            codename=codename,
            tenant=tenant,
            app=app,
            permission_category=permission_category,
            is_system_permission=False
        )
        return app

    def update(self, instance, validated_data):
        app_data = validated_data.pop('app', '')
        if app_data:
            app_uuid = app_data.get('uuid')
            app = App.active_objects.filter(uuid=app_uuid).first()
            instance.app = app
        instance.__dict__.update(validated_data)
        instance.save()
        return instance


class PermissionGroupListSerializer(DynamicFieldsModelSerializer):

    uuid = serializers.CharField(read_only=True)
    permissions = serializers.ListField(
        child=serializers.CharField(), label=_('权限列表'), source="permission_names"
    )

    class Meta:
        model = PermissionGroup

        fields = (
            'uuid',
            'name',
            'is_system_group',
            'permissions'
        )


class PermissionGroupCreateSerializer(DynamicFieldsModelSerializer):

    uuid = serializers.CharField(read_only=True)
    is_system_group = serializers.BooleanField(read_only=True, label=_('是否是系统组'))
    permissions = create_foreign_key_field(serializers.ListField)(
        model_cls=PermissionGroup,
        field_name='uuid',
        page=permission.tag,
        child=serializers.CharField(),
        default=[],
        link="permissions",
        source="permission_uuids"
    )

    class Meta:
        model = PermissionGroup

        fields = (
            'uuid',
            'name',
            'is_system_group',
            'permissions',
        )

    def create(self, validated_data):
        tenant = self.context['tenant']
        name = validated_data.get('name', '')
        permissions = validated_data.get('permission_uuids', None)
        permission_group = PermissionGroup()
        permission_group.name = name
        permission_group.is_system_group = False
        permission_group.tenant = tenant
        permission_group.save()
        if permissions is not None:
            permissions = Permission.valid_objects.filter(uuid__in=permissions)
            for permission in permissions:
                permission_group.permissions.add(permission)
        return permission_group

    def update(self, instance, validated_data):
        permissions = validated_data.pop('permission_uuids', None)
        if permissions is not None:
            instance.permissions.clear()
            permissions = Permission.valid_objects.filter(uuid__in=permissions)
            for permission in permissions:
                instance.permissions.add(permission)
        instance.__dict__.update(validated_data)
        instance.save()
        return instance
