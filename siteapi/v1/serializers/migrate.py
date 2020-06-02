'''
views for migrate
'''
from rest_framework import serializers

from oneid_meta.models import User, OrgMember
from siteapi.v1.serializers.user import OrgUserLiteSerializer
from common.django.drf.serializer import DynamicFieldsModelSerializer


class UserCSVSerializer(DynamicFieldsModelSerializer):
    '''
    serializer for user csv
    '''
    org_user = serializers.SerializerMethodField()

    class Meta:    # pylint: disable=missing-docstring
        model = User

        fields = (
            'username',
            'name',
            'private_email',
            'mobile',
            'gender',
            'avatar',
            'org_user',
        )

    def get_org_user(self, obj):
        '''
        user info in org
        '''
        org = self.context.get('org', None)
        if not org:
            return None
        org_user = OrgMember.valid_objects.filter(user=obj, owner=org).first()
        if not org_user:
            return None
        return OrgUserLiteSerializer(org_user).data

    def to_representation(self, instance):
        '''
        ...org_user
        '''
        res = super().to_representation(instance)
        org_user = res.pop('org_user', None)
        if not org_user:
            return res
        res.update(org_user)
        return res
