
from django.urls import re_path
from django.urls import path
from . import views


urlpatterns = [
    path("childaccounts/", views.ChildUserAccountListView.as_view(), name='childaccounts'),
    re_path(r'^childaccounts/(?P<account_uuid>[\w-]+)/detail/', views.ChildUserAccountDetailView.as_view(), name='childaccounts-detail'),
    re_path(r'^childaccounts/(?P<account_uuid>[\w-]+)/check_type/', views.ChildUserAccountCheckTypeView.as_view(), name='childaccounts-checktype'),
    re_path(r'^childaccounts/(?P<account_uuid>[\w-]+)/get_token/', views.ChildUserAccountGetTokenView.as_view(), name='childaccounts-get-token'),
]
