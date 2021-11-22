import json
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from .models import DataSyncConfig
from django.db.models.signals import post_save, pre_delete
from common.logger import logger


def sync_config_saved(sender, instance: DataSyncConfig, created: bool, **kwargs):
    # created or updated
    if instance.sync_mode == "client":
        if not instance.is_del:
            data = instance.data
            crontab = data.get('crontab')
            if crontab:
                try:
                    crontab = crontab.split(' ')
                    crontab.extend(['*'] * (5-len(crontab)))

                    # create CrontabSchedule
                    schedule, _ = CrontabSchedule.objects.get_or_create(
                        minute = crontab[0],
                        hour = crontab[1],
                        day_of_week = crontab[2],
                        day_of_month = crontab[3],
                        month_of_year = crontab[4],
                    )

                    # create PeriodicTask
                    PeriodicTask.objects.update_or_create(
                        name=instance.uuid,
                        defaults={'crontab': schedule, 'task': data['task'], 'kwargs': json.dumps(data)}
                    )
                except Exception as e:
                    logger.exception('add celery task failed %s' % e)
        else:
            try:
                # fake delete triggers post_save signal
                PeriodicTask.objects.filter(name=instance.uuid).delete()
            except Exception as e:
                logger.exception('delete celery task failed %s' % e)


def sync_config_deleted(sender, instance: DataSyncConfig, **kwargs):
    if instance.sync_mode == "client":
        PeriodicTask.objects.filter(name=instance.uuid).delete()


post_save.connect(receiver=sync_config_saved, sender=DataSyncConfig)

pre_delete.connect(receiver=sync_config_deleted, sender=DataSyncConfig)
