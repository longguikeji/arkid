from django.urls import path
from . import views
from .views import UsersView, GroupsView

try:
    from django.urls import re_path
except ImportError:
    from django.conf.urls import url as re_path

urlpatterns = [
    re_path(
        r'^tenant/(?P<tenant_uuid>[\w-]+)/ad/scim/Users(?:/(?P<uuid>[^/]+))?$',
        UsersView.as_view(),
        name="ad-users",
    ),
    re_path(
        r'^tenant/(?P<tenant_uuid>[\w-]+)/ad/scim/Groups(?:/(?P<uuid>[^/]+))?$',
        GroupsView.as_view(),
        name="ad-groups",
    ),
]
