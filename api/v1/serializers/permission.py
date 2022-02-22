from lib.dynamic_fields_model_serializer import DynamicFieldsModelSerializer
from common.serializer import BaseDynamicFieldModelSerializer
from django.contrib.contenttypes.models import ContentType
from inventory.models import User, Permission, PermissionGroup
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from api.v1.fields.custom import create_foreign_key_field
from ..pages import app, permission, permission_group
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
        page=app.app_only_list_tag,
        label=_('应用'),
        source="app.uuid",
        required=False,
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
        app_obj = validated_data.get('app', '')
        app_uuid = ''
        if app_obj:
            app_uuid = app_obj.get('uuid')
        codename = 'custom_{}'.format(uuid.uuid4())
        permission_category = validated_data.get('permission_category', '')
        # 新建权限
        permission = Permission()
        permission.name = name
        if app_obj:
            content_type = ContentType.objects.get_for_model(App)
            app = App.active_objects.filter(uuid=app_uuid).first()
            # 权限属性配置
            permission.content_type = content_type
            permission.app = app
        else:
            permission.content_type = None
            permission.app = None
        permission.codename = codename
        permission.tenant = tenant
        permission.permission_category = permission_category
        permission.is_system_permission = False
        permission.action = ''
        permission.operation_id = ''
        permission.description = ''
        permission.request_url = ''
        permission.request_type = ''
        permission.group_info = None
        permission.is_update = True
        permission.save()
        return permission

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


class PermissionChildSerializer(serializers.Serializer):

    uuid = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)


class PermissionGroupCreateSerializer(DynamicFieldsModelSerializer):

    uuid = serializers.CharField(read_only=True)
    is_system_group = serializers.BooleanField(read_only=True, label=_('是否是系统组'))
    permissions = create_foreign_key_field(serializers.ListField)(
        model_cls=Permission,
        field_name='uuid',
        page=permission.permission_only_list_tag,
        child=serializers.CharField(),
        default=[],
        link="permission_children",
        source="permission_uuids"
    )
    permission_children = serializers.ListField(
        child=PermissionChildSerializer(),
        read_only=True,
    )
    parent_uuid = create_foreign_key_field(serializers.CharField)(
        model_cls=PermissionGroup,
        field_name='uuid',
        page=permission_group.permission_group_only_list_tag,
        label=_('父权限分组'),
        source="parent.uuid",
        required=False,
    )

    class Meta:
        model = PermissionGroup

        fields = (
            'uuid',
            'name',
            'parent_uuid',
            'is_system_group',
            'permissions',
            'permission_children',
        )

    def create(self, validated_data):
        tenant = self.context['tenant']
        name = validated_data.get('name', '')
        permissions = validated_data.get('permission_uuids', None)
        parent = validated_data.get('parent', None)
        parent_uuid = ''
        if parent:
            parent_uuid = parent.get('uuid', '')
        permission_group = PermissionGroup()
        permission_group.name = name
        permission_group.is_system_group = False
        if parent_uuid:
            permission_group.parent = PermissionGroup.valid_objects.filter(uuid=parent_uuid).first()
        permission_group.tenant = tenant
        permission_group.save()
        if permissions is not None:
            permissions = Permission.valid_objects.filter(uuid__in=permissions)
            for permission in permissions:
                permission_group.permissions.add(permission)
        return permission_group

    def update(self, instance, validated_data):
        permissions = validated_data.pop('permission_uuids', None)
        parent = validated_data.get('parent', None)
        parent_uuid = ''
        if parent:
            parent_uuid = parent.get('uuid', '')
        if parent_uuid:
            instance.parent = PermissionGroup.valid_objects.filter(uuid=parent_uuid).first()
        if permissions is not None:
            instance.permissions.clear()
            permissions = Permission.valid_objects.filter(uuid__in=permissions)
            for permission in permissions:
                instance.permissions.add(permission)
        instance.__dict__.update(validated_data)
        instance.save()
        return instance

# user permission
class UserPermissionSerializer(serializers.Serializer):

    uuid = serializers.CharField(label=_('UUID'))
    name = serializers.CharField(label=_('名称'))
    is_system = serializers.BooleanField(read_only=True, label=_('是否是系统权限'))
    app_name = serializers.CharField(label=_('app'))
    source = serializers.CharField(label=_('来源'))


class UserPermissionListSerializer(serializers.Serializer):

    items = serializers.ListField(
        child=UserPermissionSerializer(), label=_('数据')
    )


class UserPermissionCreateSerializer(serializers.Serializer):

    permissions = create_foreign_key_field(serializers.ListField)(
        model_cls=Permission,
        field_name='uuid',
        page=permission.permission_only_list_tag,
        child=serializers.CharField(),
        default=[],
        required=False,
        link="permissions",
    )

    permission_groups = create_foreign_key_field(serializers.ListField)(
        model_cls=PermissionGroup,
        field_name='uuid',
        page=permission_group.permission_group_only_list_tag,
        child=serializers.CharField(),
        default=[],
        required=False,
        link="permission_groups",
    )

    def create(self, validated_data):
        user = self.context['user']

        permissions = validated_data.get('permissions', None)
        permission_groups = validated_data.get('permission_groups', None)

        if permissions is not None:
            permissions = Permission.valid_objects.filter(uuid__in=permissions)
            for permission in permissions:
                user.user_permissions.add(permission)
        
        if permission_groups is not None:
            permission_groups = PermissionGroup.valid_objects.filter(uuid__in=permission_groups)
            for permission_group in permission_groups:
                user.user_permissions_group.add(permission_group)
        return validated_data


class UserPermissionDeleteSerializer(serializers.Serializer):

    is_delete = serializers.BooleanField(label=_('是否成功删除'))


# group permission
class GroupPermissionSerializer(serializers.Serializer):

    uuid = serializers.CharField(label=_('UUID'))
    name = serializers.CharField(label=_('名称'))
    is_system = serializers.BooleanField(read_only=True, label=_('是否是系统权限'))
    app_name = serializers.CharField(label=_('app'))
    source = serializers.CharField(label=_('来源'))


class GroupPermissionListSerializer(serializers.Serializer):

    items = serializers.ListField(
        child=GroupPermissionSerializer(), label=_('数据')
    )


class GroupPermissionCreateSerializer(serializers.Serializer):

    permissions = create_foreign_key_field(serializers.ListField)(
        model_cls=Permission,
        field_name='uuid',
        page=permission.permission_only_list_tag,
        child=serializers.CharField(),
        default=[],
        required=False,
        link="permissions",
    )

    permission_groups = create_foreign_key_field(serializers.ListField)(
        model_cls=PermissionGroup,
        field_name='uuid',
        page=permission_group.permission_group_only_list_tag,
        child=serializers.CharField(),
        default=[],
        required=False,
        link="permission_groups",
    )

    def create(self, validated_data):
        group = self.context['group']

        permissions = validated_data.get('permissions', None)
        permission_groups = validated_data.get('permission_groups', None)

        if permissions is not None:
            permissions = Permission.valid_objects.filter(uuid__in=permissions)
            for permission in permissions:
                group.permissions.add(permission)
        
        if permission_groups is not None:
            permission_groups = PermissionGroup.valid_objects.filter(uuid__in=permission_groups)
            for permission_group in permission_groups:
                group.permissions_groups.add(permission_group)
        return validated_data


class GroupPermissionDeleteSerializer(serializers.Serializer):

    is_delete = serializers.BooleanField(label=_('是否成功删除'))


class AppPermissionSerializer(BaseDynamicFieldModelSerializer):

    is_system_permission = serializers.BooleanField(read_only=True, label=_('是否是系统权限'))

    class Meta:
        model = Permission

        fields = (
            'uuid',
            'name',
            'is_system_permission',
        )