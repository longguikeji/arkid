from django.db import migrations
from django_celery_beat.models import PeriodicTask, IntervalSchedule


def add_rm_unbonded_user(apps, schema_editor):

    interval_10min, _ = IntervalSchedule.objects.get_or_create(
        every=10,
        period=IntervalSchedule.MINUTES,
    )

    PeriodicTask.objects.get_or_create(
        name='rm_unboned_user',
        interval=interval_10min,
        task='taskapp.tasks.rm_unbonded_user_task',
        queue='dept',
        routing_key='dept',
    )


class Migration(migrations.Migration):

    dependencies = [
        ('tasksapp', '0002_add_flush_all_perm'),
    ]

    operations = [
        migrations.RunPython(add_rm_unbonded_user),
    ]
