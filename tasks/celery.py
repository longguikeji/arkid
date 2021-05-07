from celery import Celery
from django.conf import settings


app = Celery('arkid', broker=settings.CELERY_BROKER, include=[
    'tasks.tasks',
])


if __name__ == '__main__':
    app.start()
