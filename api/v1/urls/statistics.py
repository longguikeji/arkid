from django.urls import re_path

from api.v1.views import statistics


urlpatterns = [
    re_path(
        r'^tenant/(?P<tenant_uuid>[\w-]+)/statistics/',
        statistics.StatisticsView.as_view(),
        name='statistics',
    ),
]
