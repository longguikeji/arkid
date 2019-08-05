from django.db import migrations
from django_celery_beat.models import PeriodicTask, IntervalSchedule


def add_flush_all_perm_task(apps, schema_editor):

    interval_5min, _ = IntervalSchedule.objects.get_or_create(
        every=5,
        period=IntervalSchedule.MINUTES,
    )

    PeriodicTask.objects.get_or_create(
        name='flush_all_perm_in_db',
        interval=interval_5min,
        task='tasksapp.tasks.flush_all_perm_in_db',
        queue='perm',
        routing_key='perm',
    )

    flush_user_perm, _ = PeriodicTask.objects.get_or_create(
        name='flush_user_perm_in_db',
        interval=interval_5min,
        task='tasksapp.tasks.flush_user_perm_in_db',
        queue='perm',
        routing_key='perm',
    )
    flush_user_perm.enabled = False
    flush_user_perm.save()


class Migration(migrations.Migration):

    dependencies = [
        ('tasksapp', '0001_add_default_periodic_task'),
    ]

    operations = [
        migrations.RunPython(add_flush_all_perm_task),
    ]