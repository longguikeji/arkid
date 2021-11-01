from django.urls.conf import re_path
from .views import AppSubscribe, AppSubscribeList, SubscribeAppList
urlpatterns = [
    re_path(
        r'app/(?P<app_id>[\w-]+)/subscribe/',
        AppSubscribe.as_view(),
        name="app_subscribe"
    ),
    re_path(
        r'/app_subscribe_list/',
        AppSubscribeList.as_view(),
        name="app_subscribe_list"
    ),
    re_path(
        r'/subscribed_app_list/',
        SubscribeAppList.as_view(),
        name="subscribed_app_list"
    ),
]
