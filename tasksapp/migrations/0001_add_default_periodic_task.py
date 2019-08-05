from django.db import migrations
from django_celery_beat.models import PeriodicTask, IntervalSchedule

def add_default_periodic_task(apps, schema_editor):

    interval_5min, _ = IntervalSchedule.objects.get_or_create(
        every=5,
        period=IntervalSchedule.MINUTES,
    )

    PeriodicTask.objects.get_or_create(
        name='flush_user_perm_in_db',
        interval=interval_5min,
        task='tasksapp.tasks.flush_user_perm_in_db',
        queue='perm',
        routing_key='perm',
    )

    PeriodicTask.objects.get_or_create(
        name='flush_user_perm_in_ldap',
        interval=interval_5min,
        task='tasksapp.tasks.flush_user_perm_in_ldap',
        queue='perm',
        routing_key='perm',
    )

    PeriodicTask.objects.get_or_create(
        name='aggregate_user_in_ldap_dept',
        interval=interval_5min,
        task='tasksapp.tasks.aggregate_user_in_ldap_dept',
        queue='dept',
        routing_key='dept',
    )

    PeriodicTask.objects.get_or_create(
        name='aggregate_user_in_ldap_group',
        interval=interval_5min,
        task='tasksapp.tasks.aggregate_user_in_ldap_group',
        queue='group',
        routing_key='group',
    )


class Migration(migrations.Migration):

    dependencies = [
        ('oneid_meta', '0010_auto_20190129_1556'),
    ]

    operations = [
        migrations.RunPython(add_default_periodic_task),
    ]
