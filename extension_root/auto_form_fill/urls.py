from django.urls import re_path
from django.urls import path
from . import views


urlpatterns = [
    re_path(
        r"^tenant/(?P<tenant_uuid>[\w-]+)/user_app_account/",
        views.UserAppAccountListView.as_view(),
        name='user-app-account-list',
    ),
    re_path(
        r"^tenant/(?P<tenant_uuid>[\w-]+)/user_app_account/(?P<account_uuid>[\w-]+)/",
        views.UserAppAccountDetailView.as_view(),
        name='user-app-account-list',
    ),
]
