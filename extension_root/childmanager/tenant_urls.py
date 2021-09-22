
from django.urls import re_path
from django.urls import path
from . import views


urlpatterns = [
    path("childmanager/", views.ChildManagerListView.as_view(), name='tenant-childmanager'),
    path("childmanager/create", views.ChildManagerCreateView.as_view(), name='tenant-childmanager-create'),
    re_path(r'^childmanager/(?P<childmanager_uuid>[\w-]+)/detail/', views.ChildManagerDetailView.as_view(), name='tenant-childmanager-detail'),
]
