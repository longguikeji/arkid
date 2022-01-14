from django.urls.conf import re_path
from .views import MessageAdd

urlpatterns = [
    re_path(
        r'app/(?P<app_id>[\w-]+)/message_add/',
        MessageAdd.as_view(),
        name="app_message_add"
    ),
]
