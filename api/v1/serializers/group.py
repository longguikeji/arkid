from inspect import Parameter
from common.serializer import BaseDynamicFieldModelSerializer
from inventory.models import Group, Permission
from rest_framework import serializers
from drf_spectacular.utils import extend_schema, extend_schema_view
from api.v1.fields.custom import create_foreign_key_field, create_foreign_field
from .permission import PermissionSerializer
from ..pages import group, permission
from django.utils.translation import gettext_lazy as _
from webhook.manager import WebhookManager
from django.db import transaction

import uuid


class GroupBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('name', 'uuid')


class GroupSerializer(BaseDynamicFieldModelSerializer):

    parent = GroupBaseSerializer(read_only=True, many=False)
    parent_uuid = create_foreign_key_field(serializers.UUIDField)(
        model_cls=Group,
        field_name='uuid',
        page=group.group_tree_tag,
        label='上级组织',
        source='parent.uuid',
        default=None,
        link="parent",
    )

    parent_name = create_foreign_field(serializers.CharField)(
        model_cls=Group,
        field_name='name',
        page=group.group_tree_tag,
        label='上级组织',
        read_only=True,
        source='parent.name',
        default=None,
    )

    children = serializers.SerializerMethodField()
    # permissions = serializers.SerializerMethodField()

    # set_permissions = create_foreign_key_field(serializers.ListField)(
    #     model_cls=Permission,
    #     field_name='uuid',
    #     page=permission.tag,
    #     child=serializers.CharField(),
    #     write_only=True,
    #     default=[],
    #     link="permissions",
    # )

    class Meta:
        model = Group

        fields = (
            'id',
            'uuid',
            'name',
            'parent',
            'parent_uuid',
            'parent_name',
            # 'permissions',
            'children',
            # 'set_permissions',
        )

        extra_kwargs = {'parent_uuid': {'blank': True}}

    # def get_permissions(self, instance):
    #     permissions = instance.permissions.all()
    #     ret = []
    #     for p in permissions:
    #         o = PermissionSerializer(p)
    #         ret.append(o.data)
    #     return ret

    @transaction.atomic()
    def create(self, validated_data):
        name = validated_data.get('name')
        parent_uuid = validated_data.get('parent').get('uuid')
        tenant = self.context['tenant']

        # set_permissions = validated_data.pop('set_permissions', None)

        parent = Group.valid_objects.filter(uuid=parent_uuid).first()

        o: Group = Group.valid_objects.create(tenant=tenant, name=name, parent=parent)

        # 新建分组权限
        permission_obj = Permission()
        permission_obj.name = name
        permission_obj.tenant = tenant
        permission_obj.app = None
        permission_obj.codename = 'group_{}'.format(uuid.uuid4())
        permission_obj.permission_category = '数据'
        permission_obj.is_system_permission = True
        permission_obj.action = ''
        permission_obj.operation_id = ''
        permission_obj.description = ''
        permission_obj.request_url = ''
        permission_obj.request_type = ''
        permission_obj.group_info = o
        permission_obj.is_update = True
        permission_obj.save()
        # if set_permissions is not None:
        #     o.permissions.clear()
        #     for p_uuid in set_permissions:
        #         p = Permission.objects.filter(uuid=p_uuid).first()
        #         if p is not None:
        #             o.permissions.add(p)

        transaction.on_commit(
            lambda: WebhookManager.group_created(self.context['tenant'].uuid, o)
        )
        return o

    @transaction.atomic()
    def update(self, instance: Group, validated_data):
        name = validated_data.get('name', None)
        parent_uuid = validated_data.get('parent', {}).get('uuid', None)

        # set_permissions = validated_data.pop('set_permissions', None)

        if name is not None:
            instance.name = name

        if parent_uuid is not None:
            parent = Group.valid_objects.filter(uuid=parent_uuid).first()
            instance.parent = parent

        # 更新分组权限
        # if set_permissions is not None:
        #     instance.permissions.clear()
        #     for p_uuid in set_permissions:
        #         p = Permission.objects.filter(uuid=p_uuid).first()
        #         if p is not None:
        #             instance.permissions.add(p)
        # else:
        #     instance.permissions.clear()

        instance.save()

        permission_obj = Permission.valid_objects.filter(
            tenant=instance.tenant,
            app=None,
            permission_category='数据',
            is_system_permission=True,
            group_info=instance,
        ).first()
        if permission_obj is None:
            permission_obj = Permission()
            permission_obj.name = instance.name
            permission_obj.tenant = instance.tenant
            permission_obj.codename = 'group_{}'.format(uuid.uuid4())
            permission_obj.app = None
            permission_obj.permission_category = '数据'
            permission_obj.is_system_permission = True
            permission_obj.action = ''
            permission_obj.operation_id = ''
            permission_obj.description = ''
            permission_obj.request_url = ''
            permission_obj.request_type = ''
            permission_obj.group_info = instance
            permission_obj.is_update = True
            permission_obj.save()
        # 可能会更新名称
        permission_obj.name = instance.name
        permission_obj.save()

        transaction.on_commit(
            lambda: WebhookManager.group_updated(self.context['tenant'].uuid, instance)
        )
        return instance

    def get_children(self, instance):
        qs = Group.valid_objects.filter(parent=instance).order_by('id')
        return [GroupBaseSerializer(q).data for q in qs]


# for openapi


class GroupListResponseSerializer(GroupSerializer):
    class Meta:
        model = Group
        fields = ('name', 'parent_name', 'uuid', 'children')


class GroupCreateRequestSerializer(GroupSerializer):
    class Meta:
        model = Group
        fields = (
            'uuid',
            'name',
            'parent_uuid',
            # 'permissions',
            # 'set_permissions',
        )


class GroupCreateResponseSerializer(GroupSerializer):
    class Meta:
        model = Group
        fields = (
            'uuid',
            'name',
            'parent',
            'parent_uuid',
            'parent_name',
        )


class GroupImportSerializer(serializers.Serializer):

    file = serializers.FileField(label=_('上传文件'), write_only=True)
    error = serializers.CharField(read_only=True)
    message = serializers.CharField(read_only=True)
