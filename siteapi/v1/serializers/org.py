'''
serializers for org
'''

# pylint: disable=missing-class-docstring, abstract-method

from rest_framework import serializers

from common.django.middleware import CrequestMiddleware
from common.django.drf.serializer import DynamicFieldsModelSerializer
from oneid_meta.models import Org


class OrgDeserializer(serializers.Serializer):
    '''
    deserializer for org
    '''
    name = serializers.CharField(required=True)

    def create(self, validated_data):
        owner = self.context['request'].user
        validated_data['owner'] = owner
        org = Org.create(**validated_data)
        return org


class OrgSerializer(DynamicFieldsModelSerializer):
    '''
    serializer for org
    '''
    oid = serializers.CharField(source='oid_str')
    owner = serializers.CharField(source='owner.username')
    dept_uid = serializers.CharField(source='dept.uid')
    group_uid = serializers.CharField(source='group.uid')
    direct_uid = serializers.CharField(source='direct.uid')
    manager_uid = serializers.CharField(source='manager.uid')
    app_group_uid = serializers.CharField(source='app_group.uid')
    default_app_group_uid = serializers.CharField(source='default_app_group.uid')
    role_uid = serializers.CharField(source='role.uid')
    label_uid = serializers.CharField(source='label.uid')
    role = serializers.SerializerMethodField()

    class Meta:
        model = Org
        fields = (
            'oid',
            'name',
            'owner',
            'dept_uid',
            'group_uid',
            'direct_uid',
            'manager_uid',
            'app_group_uid',
            'default_app_group_uid',
            'role_uid',
            'label_uid',
            'role',
        )

    def get_role(self, instance):    # pylint: disable=no-self-use
        '''
        当前用户在该组织的角色：
        - member - 普通成员
        - manager - 子管理员
        - owner - 创建者，唯一管理员
        - '' - 未知
        '''
        request = CrequestMiddleware.get_request()
        if request:
            return instance.get_user_role(request.user)
        return ""
