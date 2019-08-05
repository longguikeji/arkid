'''
serializers

为避免循环引用，部分共用Serializer置于该文件
'''
from rest_framework import serializers
from common.django.drf.serializer import DynamicFieldsModelSerializer

from oneid_meta.models import User


class UserLiteSerializer(DynamicFieldsModelSerializer):
    '''
    Serializer for User with basic info
    '''
    user_id = serializers.IntegerField(source='id')

    class Meta:    # pylint: disable=missing-docstring
        model = User

        fields = (
            'user_id',
            'username',
            'name',
        )
