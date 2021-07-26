from inspect import Parameter
from common.serializer import BaseDynamicFieldModelSerializer
from inventory.models import Group, Permission
from rest_framework import serializers
from drf_spectacular.utils import extend_schema, extend_schema_view
from api.v1.fields.custom import create_foreign_key_field, create_foreign_field
from .permission import PermissionSerializer
from ..pages import group, permission
from django.utils.translation import gettext_lazy as _


class GroupBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('name', 'uuid')


class GroupSerializer(BaseDynamicFieldModelSerializer):

    parent = GroupBaseSerializer(read_only=True, many=False)
    parent_uuid = create_foreign_key_field(serializers.UUIDField)(
        model_cls=Group,
        field_name='uuid',
        page=group.group_tag,
        label='上级组织',
        source='parent.uuid',
        default=None,
    )

    parent_name = create_foreign_field(serializers.CharField)(
        model_cls=Group,
        field_name='name',
        page=group.group_tag,
        label='上级组织',
        read_only=True,
        source='parent.name',
        default=None,
    )

    children = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    set_permissions = create_foreign_key_field(serializers.ListField)(
        model_cls=Permission,
        field_name='uuid',
        page=permission.tag,
        child=serializers.CharField(),
        write_only=True,
        default=[],
    )

    class Meta:
        model = Group

        fields = (
            'id',
            'uuid',
            'name',
            'parent',
            'parent_uuid',
            'parent_name',
            'permissions',
            'children',
            'set_permissions',
        )

        extra_kwargs = {'parent_uuid': {'blank': True}}

    def get_permissions(self, instance):
        permissions = instance.permissions.all()
        ret = []
        for p in permissions:
            o = PermissionSerializer(p)
            ret.append(o.data)

        return ret

    def create(self, validated_data):
        name = validated_data.get('name')
        parent_uuid = validated_data.get('parent').get('uuid')
        tenant = self.context['tenant']

        set_permissions = validated_data.pop('set_permissions', None)

        parent = Group.valid_objects.filter(uuid=parent_uuid).first()

        o: Group = Group.valid_objects.create(tenant=tenant, name=name, parent=parent)

        if set_permissions is not None:
            o.permissions.clear()
            for p_uuid in set_permissions:
                p = Permission.objects.filter(uuid=p_uuid).first()
                if p is not None:
                    o.permissions.add(p)

        return o

    def update(self, instance: Group, validated_data):
        name = validated_data.get('name', None)
        parent_uuid = validated_data.get('parent', {}).get('uuid', None)

        set_permissions = validated_data.pop('set_permissions', None)

        if name is not None:
            instance.name = name

        if parent_uuid is not None:
            parent = Group.valid_objects.filter(uuid=parent_uuid).first()
            instance.parent = parent

        if set_permissions is not None:
            instance.permissions.clear()
            for p_uuid in set_permissions:
                p = Permission.objects.filter(uuid=p_uuid).first()
                if p is not None:
                    instance.permissions.add(p)
        else:
            instance.permissions.clear()

        instance.save()
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
            'permissions',
            'set_permissions',
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
