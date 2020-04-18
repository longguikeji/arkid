'''
views for migrate
'''

from ....oneid_meta.models import User
from ....common.django.drf.serializer import DynamicFieldsModelSerializer


class UserCSVSerializer(DynamicFieldsModelSerializer):
    '''
    serializer for user csv
    '''
    class Meta:    # pylint: disable=missing-docstring
        model = User

        fields = (
            'username',
            'name',
            'email',
            'private_email',
            'mobile',
            'gender',
            'avatar',
            'position',
            'employee_number',
        )
