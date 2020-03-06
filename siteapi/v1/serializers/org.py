'''
serializers for org
'''

# pylint: disable=missing-class-docstring, abstract-method

from rest_framework.serializers import Serializer, CharField

from common.django.drf.serializer import DynamicFieldsModelSerializer
from oneid_meta.models import Org


class OrgDeserializer(Serializer):
    '''
    deserializer for org
    '''
    name = CharField()


class OrgSerializer(DynamicFieldsModelSerializer):
    '''
    serializer for org
    '''
    oid = CharField(source='oid_str')
    owner = CharField(source='owner.username')
    dept_uid = CharField(source='dept.uid')
    group_uid = CharField(source='group.uid')
    direct_uid = CharField(source='direct.uid')
    manager_uid = CharField(source='manager.uid')
    role_uid = CharField(source='role.uid')
    label_uid = CharField(source='label.uid')

    class Meta:
        model = Org
        fields = ('oid', 'name', 'owner', 'dept_uid', 'group_uid', 'direct_uid', 'manager_uid', 'role_uid', 'label_uid')
