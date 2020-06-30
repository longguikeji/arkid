'''
serializers

为避免循环引用，部分共用Serializer置于该文件
'''
from rest_framework import serializers
from common.django.drf.serializer import DynamicFieldsModelSerializer

from oneid_meta.models import User, APP


class UserLiteSerializer(DynamicFieldsModelSerializer):
    '''
    Serializer for User with basic info
    '''
    user_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:    # pylint: disable=missing-docstring
        model = User

        fields = (
            'user_id',
            'username',
            'name',
        )


class AppLiteSerializer(DynamicFieldsModelSerializer):
    """
    Serializer for App with basic info
    """
    app_id = serializers.IntegerField(source='id', read_only=True)
    uid = serializers.CharField(read_only=True)

    class Meta:    # pylint: disable=missing-docstring
        model = APP

        fields = (
            'app_id',
            'uid',
            'name',
            'remark',
        )
