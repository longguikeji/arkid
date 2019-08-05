'''
serializer for task result
'''

from django_celery_results.models import TaskResult
from celery import states
from rest_framework import serializers

from common.django.drf.serializer import DynamicFieldsModelSerializer

WAITING = (
    states.RETRY,
    states.PENDING,
    states.RECEIVED,
)
DOING = (states.STARTED, )
FAILED = (
    states.FAILURE,
    states.REJECTED,
    states.REVOKED,
)
SUCCESS = (states.SUCCESS, )

PRECEDENCE = [
    WAITING,
    DOING,
    FAILED,
    SUCCESS,
]

STATUS_LOOKUP = dict((state, index + 1) for index, state_set in enumerate(PRECEDENCE) for state in state_set)


class TaskResultSerializer(DynamicFieldsModelSerializer):
    '''
    serializer for TaskResult
    '''

    status_raw = serializers.CharField(source='status')
    status = serializers.SerializerMethodField()

    class Meta:    # pylint: disable=missing-docstring
        model = TaskResult

        fields = (
            'result',
            'status',
            'status_raw',
        )

    def get_status(self, instance):    # pylint: disable=no-self-use
        '''
        simplify status
        '''
        return STATUS_LOOKUP[instance.status]
