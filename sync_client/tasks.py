import json
import sync_client
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from sync_client.sync import get_ldap_config
from sync_client.sync import sync as ldap_sync
from common.logger import logger
from celery import shared_task


def create_task():
    settings = get_ldap_config()
    if not settings or not settings.get('cron_jobs'):
        logger.info('no cron jobs configured for sync_client')
        return
    cron_jobs = settings["cron_jobs"]
    logger.info(f'cron jobs: {cron_jobs} configured for sync_client')

    # remove old tasks and schedules
    PeriodicTask.objects.all().delete()
    CrontabSchedule.objects.all().delete()

    for cron_job in cron_jobs:
        # create CrontabSchedule
        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute=cron_job.get('minute','0'),
            hour=cron_job['hour'],
            day_of_week=cron_job.get('day_of_week', '*'),
            day_of_month=cron_job.get('day_of_month', '*'),
            month_of_year=cron_job.get('month_of_year', '*'),
        )

        # create PeriodicTask
        PeriodicTask.objects.create(
            crontab=schedule,          # we created this above.
            name=cron_job['name'],     # simply describes this periodic task.
            task=cron_job['task'],     # name of task.
            kwargs=json.dumps(cron_job)
        )


@shared_task(bind=True)
def sync(self, *args, **kwargs):
    try:
        ldap_sync()
    except Exception as exc:
        max_retries = kwargs.get('max_retries', 3)
        countdown = kwargs.get('retry_delay', 5*60)
        raise self.retry(exc=exc, max_retries=max_retries, countdown=countdown)
