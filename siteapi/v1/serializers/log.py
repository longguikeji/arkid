'''
serializers for Log
'''
from rest_framework import serializers

from common.django.drf.serializer import DynamicFieldsModelSerializer
from oneid_meta.models import Log
from siteapi.v1.serializers.user import UserLiteSerializer


class LogLiteSerializer(DynamicFieldsModelSerializer):
    '''
    lite serializer for log
    '''

    user = serializers.SerializerMethodField()
    uuid = serializers.UUIDField(format='hex', read_only=True)

    class Meta:    # pylint: disable=missing-docstring
        model = Log

        fields = (
            'uuid',
            'created',
            'user',
            'subject',
            'summary',
            'subject_verbose',
        )

    def get_user(self, instance):
        if instance.user:
            return UserLiteSerializer(instance.user).data
        return {'username': 'unknown', 'name': 'unknown'}


class LogSerializer(LogLiteSerializer):
    '''
    serializer for log
    '''
    class Meta:    # pylint: disable=missing-docstring
        model = Log

        fields = (
            'uuid',
            'created',
            'user',
            'subject',
            'summary',
            'subject_verbose',
            'detail',
        )
