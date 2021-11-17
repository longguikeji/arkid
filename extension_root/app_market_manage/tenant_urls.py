from django.conf.urls import url
from django.urls.conf import re_path
from .views import AppSubscribe, AppSubscribeList, SubscribeAppList

urlpatterns = [
    re_path(
        r'app/(?P<app_id>[\w-]+)/user/(?P<user_id>[\w-]+)/subscribe/',
        AppSubscribe.as_view(),
        name="app_subscribe"
    ),
    url(
        r'user/(?P<user_id>[\w-]+)/app_subscribe_list/',
        AppSubscribeList.as_view(),
        name="app_subscribe_list"
    ),
    re_path(
        r'user/(?P<user_id>[\w-]+)/subscribed_app_list/',
        SubscribeAppList.as_view(),
        name="subscribed_app_list"
    ),
]
