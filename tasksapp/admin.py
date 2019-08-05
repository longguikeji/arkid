from django.contrib import admin

from django_celery_results.models import TaskResult
from django_celery_results.admin import TaskResultAdmin


class MyTaskResultAdmin(TaskResultAdmin):
    """Admin-interface for results of tasks."""

    list_filter = ('status',)


admin.site.unregister(TaskResult)
admin.site.register(TaskResult, MyTaskResultAdmin)
