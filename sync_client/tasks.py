import sync_client
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from sync_client.sync import get_ldap_config
from sync_client.sync import sync as ldap_sync
from common.logger import logger
from celery import shared_task


def create_task():
    settings = get_ldap_config()
    if not settings or not settings.get('cron_job'):
        logger.info('no cron jobs configured for sync_client')
        return
    cron_job = settings["cron_job"]
    logger.info(f'cron jobs: {cron_job} configured for sync_client')

    # remove old tasks and schedules
    PeriodicTask.objects.all().delete()
    CrontabSchedule.objects.all().delete()

    # create CrontabSchedule
    schedule, _ = CrontabSchedule.objects.get_or_create(
        minute=cron_job.get('minute','0'),
        hour=cron_job['hour'],
        day_of_week=cron_job.get('day_of_week', '*'),
        day_of_month=cron_job.get('day_of_month', '*'),
        month_of_year=cron_job.get('month_of_year', '*'),
    )

    # create PeriodicTask
    PeriodicTask.objects.get_or_create(
        crontab=schedule,          # we created this above.
        name='Sync form scim to active diretory',      # simply describes this periodic task.
        task=cron_job['task'],      # name of task.
    )


@shared_task
def sync():
    ldap_sync()
