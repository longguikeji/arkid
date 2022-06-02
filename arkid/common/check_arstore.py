from django_celery_beat.models import PeriodicTask, CrontabSchedule
from arkid.common.logger import logger
import json
from django.db.utils import OperationalError


def check_extensions_expired():
    try:
        # create CrontabSchedule
        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute="0",
            hour="2",
            day_of_week="*",
            day_of_month="*",
            month_of_year="*",
        )

        # create PeriodicTask
        PeriodicTask.objects.update_or_create(
            name='check_extension_expired',
            defaults={
                'crontab': schedule,
                'task': 'arkid.core.tasks.check_extensions_expired',
                'args': json.dumps([]),
                'kwargs': json.dumps({}),
            },
        )
    except OperationalError:
        pass
    except Exception as e:
        logger.error('add celery task failed %s' % e)