from django.db import migrations
from django_celery_beat.models import PeriodicTask, IntervalSchedule

def rm_ldap_tasks(apps, schema_editor):
    for task_name in [
        'flush_user_perm_in_ldap',
        'aggregate_user_in_ldap_dept',
        'aggregate_user_in_ldap_group',
    ]:
        task = PeriodicTask.objects.filter(name=task_name).first()
        if task:
            task.enabled = False
            task.save()

class Migration(migrations.Migration):

    dependencies = [
        ('tasksapp', '0003_add_rm_unbonded_user'),
    ]

    operations = [
        migrations.RunPython(rm_ldap_tasks),
    ]
