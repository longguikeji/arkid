'''
entrypoint of celery
'''

import os

from celery import Celery
from django.conf import settings

# 此时显式声明，从当前目录导入；否则会从三方库中导入
import oauth2_provider    # pylint: disable=unused-import

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oneid.settings')
app = Celery(    # pylint: disable=invalid-name
    'oneid',
    include={
        'tasksapp.tasks',
        'ldap.sql_backend.scripts',
        'plugins.crontab.tasks',
    },
)
app.config_from_object(settings, namespace='CELERY')
