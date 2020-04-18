'''
serializer for advanced feature
'''

from croniter import croniter
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django_celery_beat.models import CrontabSchedule, PeriodicTask

from common.django.drf.serializer import DynamicFieldsModelSerializer
from oneid_meta.models import CrontabPlugin, MiddlewarePlugin


class CrontabPluginSerializer(DynamicFieldsModelSerializer):
    '''
    serializer for CrontabPlugin
    '''

    uuid = serializers.UUIDField(format='hex', read_only=True)

    class Meta:    # pylint: disable=missing-docstring
        model = CrontabPlugin

        fields = (
            'is_active',
            'uuid',
            'name',
            'detail',
            'import_path',
            'schedule',
        )

        read_only_fields = (
            'uuid',
            'import_path',
        )

    def update(self, instance, validated_data):
        instance.__dict__.update(validated_data)
        if instance.is_active and not instance.schedule:
            raise ValidationError({'schedule': ['this field is required']})

        instance.save()

        task, _ = PeriodicTask.objects.get_or_create(task=instance.import_path + '.main', )

        minute, hour, day_of_week, day_of_month, month_of_year = instance.schedule.split(' ')
        crontab_schedule, _ = CrontabSchedule.objects.get_or_create(    # pylint: disable=no-member
            minute=minute,
            hour=hour,
            day_of_week=day_of_week,
            day_of_month=day_of_month,
            month_of_year=month_of_year,
        )
        task.crontab = crontab_schedule

        if instance.is_active:
            task.enabled = True
        else:
            task.enabled = False

        task.save()
        return instance

    @staticmethod
    def validate_schedule(value):
        '''
        校验 schedule 是否合法
        '''
        if croniter.is_valid(value):
            return value
        raise ValidationError


class MiddlewarePluginSerializer(DynamicFieldsModelSerializer):
    '''
    serializer for MiddlewarePlugin
    '''
    class Meta:    # pylint: disable=missing-docstring
        model = MiddlewarePlugin
