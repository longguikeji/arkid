from django.db import migrations
from django_celery_beat.models import PeriodicTask, IntervalSchedule

def maintain_entries(apps, schema_editor):
    '''
    维护 ldap entry
    - group
    - dept
    - user
    '''

    interval_10min, _ = IntervalSchedule.objects.get_or_create(
        every=10,
        period=IntervalSchedule.MINUTES,
    )

    PeriodicTask.objects.get_or_create(
        name='sql_ldap_entry',
        interval=interval_10min,
        task='ldap.sql_backend.scripts.flush_entries',
        queue='sql_ldap',
        routing_key='sql_ldap',
    )

    PeriodicTask.objects.get_or_create(
        name='dingtalk_entry',
        interval=interval_10min,
        task='tasksapp.task.sync_ding',
        queue='sql_ding',
        routing_key='sql_ding',
    )


class Migration(migrations.Migration):

    dependencies = [
        ('sql_backend', '0005_groupOfNames'),
    ]

    operations = [
        migrations.RunPython(maintain_entries),
    ]
