#!/usr/bin/env python3

import os

from celery import Celery, bootsteps
from click import Option
from datetime import timedelta
from arkid.common.logger import logger

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arkid.settings')

app = Celery('arkid')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')


class MyBootstep(bootsteps.Step):
    def __init__(self, parent, **options):
        super().__init__(parent, **options)
        # from arkid.core.tasks.tasks import init_core_code

        dispatch_task.delay('init_core_code')


app.steps['worker'].add(MyBootstep)

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.update(
    CELERYBEAT_SCHEDULE={
        'add-arkstore-3-hours': {
            'task': 'arkid.core.tasks.celery.dispatch_task',
            'schedule': timedelta(hours=3),
            'args': ('get_arkstore_category_http',),
        },
    }
)


@app.task(bind=True)
def dispatch_task(self, task_name, *args, **kwargs):
    # logger.info(f'=== Dispatch task：{task_name}, args: {args}, kwargs: {kwargs}')
    for name, task in app.tasks.items():
        func_name = name.split('.')[-1]
        if func_name == task_name:
            logger.info(f"Ready to apply_async funtion {name}")
            task.apply_async(args, kwargs)
            break
    else:
        logger.info(f"*** Warning! No task found for name {task_name} ***")
