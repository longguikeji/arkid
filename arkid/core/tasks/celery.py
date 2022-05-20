#!/usr/bin/env python3

import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arkid.settings')

app = Celery('arkid')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


from arkid.core.tasks import tasks

# class ReadyCelery(object):

#     def __init__(self):
#         print('你被执行了')
#         from arkid.core.models import Tenant
#         from arkid.core.event import Event, dispatch_event, APP_START
#         tenant, _ = Tenant.objects.get_or_create(
#             slug='',
#             name="platform tenant",
#         )
#         dispatch_event(Event(tag=APP_START, tenant=tenant))

# ReadyCelery()
