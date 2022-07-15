#!/usr/bin/env python3

import os

from celery import Celery, bootsteps
from click import Option

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arkid.settings')

app = Celery('arkid')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

app.user_options['worker'].add(Option(('--is-init-permission',), is_flag=False, help='init permission option.'))

class MyBootstep(bootsteps.Step):

    def __init__(self, parent, is_init_permission=False, **options):
        super().__init__(parent, **options)
        if is_init_permission:
            from arkid.core.tasks.tasks import update_system_permission
            update_system_permission.delay()
            # 预置
            from arkid.core import preset_approve_action

class BindTenantBootstep(bootsteps.Step):

    def __init__(self, parent, **options):
        super().__init__(parent, **options)
        from django.conf import settings
        if not settings.IS_CENTRAL_ARKID:
            from arkid.core.tasks.tasks import bind_arkid_saas_all_tenants
            bind_arkid_saas_all_tenants.delay()

app.steps['worker'].add(MyBootstep)
app.steps['worker'].add(BindTenantBootstep)

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


from arkid.core.tasks import tasks
