'''
serializers for org
'''

# pylint: disable=abstract-method

from rest_framework.serializers import Serializer, CharField

from common.django.drf.serializer import DynamicFieldsModelSerializer
from oneid_meta.models import Org


class OrgDeserializer(Serializer):
    name = CharField()


class OrgSerializer(DynamicFieldsModelSerializer):
    oid = CharField(source='oid_str')
    dept_uid = CharField(source='dept.uid')
    group_uid = CharField(source='group.uid')
    direct_uid = CharField(source='direct.uid')
    manager_uid = CharField(source='manager.uid')
    role_uid = CharField(source='role.uid')
    label_uid = CharField(source='label.uid')

    class Meta:
        model = Org
        fields = ('oid', 'name', 'dept_uid', 'group_uid', 'direct_uid', 'manager_uid', 'role_uid', 'label_uid')
