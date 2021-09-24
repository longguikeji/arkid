from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import BaseDynamicFieldModelSerializer
from extension_root.childmanager.models import ChildManager
from api.v1.fields.custom import create_foreign_key_field
from api.v1.pages import user, group, permission
from inventory.models import User, Group, Permission

import json


class ChildManagerListSerializer(BaseDynamicFieldModelSerializer):

    name = serializers.CharField(label=_('成员名称'))
    manager_visible = serializers.ListField(
        child=serializers.CharField(), label=_('管理范围')
    )
    manager_permission = serializers.CharField(label=_('管理权限'))
    assign_permission = serializers.ListField(
        child=serializers.CharField(), label=_('权限')
    )

    class Meta:
        model = ChildManager

        fields = (
            'uuid',
            'name',
            'manager_visible',
            'manager_permission',
            'assign_permission',
        )

        extra_kwargs = {
            'uuid': {'read_only': True},
        }


class ChildManagerItemSerializer(serializers.Serializer):
    
    manager_visible = serializers.MultipleChoiceField(
        choices=(('所在分组', '所在分组的下级分组', '指定分组与账号')), label=_('管理分组范围')
    )
    manager_permission = serializers.ChoiceField(
        choices=(('全部权限', '指定权限', '所有应用权限')), label=_('允许管理哪些权限')
    )
    assign_group = create_foreign_key_field(serializers.ListField)(
        model_cls=Group,
        field_name='uuid',
        page=group.group_tree_tag,
        child=serializers.CharField(),
        required=False,
        default=[],
        label=_('指定的分组'),
    )
    assign_user = create_foreign_key_field(serializers.ListField)(
        model_cls=User,
        field_name='uuid',
        page=user.user_table_tag,
        child=serializers.CharField(),
        required=False,
        default=[],
        label=_('指定的人员'),
    )
    assign_permission = create_foreign_key_field(serializers.ListField)(
        model_cls=Permission,
        field_name='uuid',
        page=permission.permission_only_list_tag,
        child=serializers.CharField(),
        required=False,
        default=[],
        label=_('指定的权限'),
    )


class ChildManagerSerializer(BaseDynamicFieldModelSerializer):

    user_uuid = create_foreign_key_field(serializers.CharField)(
        model_cls=User,
        field_name='uuid',
        page=user.user_table_tag,
        label=_('用户'),
        source="user.uuid",
    )
    data = ChildManagerItemSerializer(label=_('相关配置'))

    class Meta:
        model = ChildManager

        fields = (
            'uuid',
            'user_uuid',
            'data',
        )

        extra_kwargs = {
            'uuid': {'read_only': True},
        }

    def create(self, validated_data):
        user_uuid = validated_data.pop('user').get('uuid')
        data = validated_data.pop('data')
        tenant = self.context['tenant']
        manager_visible = list(data.get('manager_visible'))
        manager_permission = data.get('manager_permission')
        assign_group = data.get('assign_group')
        assign_user = data.get('assign_user')
        assign_permission = data.get('assign_permission')
        obj = {
            'manager_visible': manager_visible,
            'manager_permission': manager_permission,
            'assign_group': assign_group,
            'assign_user': assign_user,
            'assign_permission': assign_permission,
        }
        childmanager = ChildManager()
        childmanager.user = User.valid_objects.filter(uuid=user_uuid).first()
        childmanager.data = obj
        childmanager.tenant = tenant
        childmanager.save()
        return childmanager
    
    def update(self, instance, validated_data):
        user_uuid = validated_data.pop('user').get('uuid')
        data = validated_data.pop('data')
        tenant = self.context['tenant']
        manager_visible = list(data.get('manager_visible'))
        manager_permission = data.get('manager_permission')
        assign_group = data.get('assign_group')
        assign_user = data.get('assign_user')
        assign_permission = data.get('assign_permission')
        obj = {
            'manager_visible': manager_visible,
            'manager_permission': manager_permission,
            'assign_group': assign_group,
            'assign_user': assign_user,
            'assign_permission': assign_permission,
        }
        instance.user = User.valid_objects.filter(uuid=user_uuid).first()
        instance.data = obj
        instance.tenant = tenant
        instance.save()
        return instance