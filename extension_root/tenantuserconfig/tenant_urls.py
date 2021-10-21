
from django.urls import re_path
from django.urls import path
from . import views


urlpatterns = [
    path("userconfig/editfields", views.TenantUserEditFieldListConfigView.as_view(), name='tenant-userconfig-editfields'),
    path("userconfig/logout", views.TenantUserLogOutConfigView.as_view(), name='tenant-userconfig-logout'),
    path("userconfig/logging", views.TenantUserLoggingConfigView.as_view(), name='tenant-userconfig-logging'),
    path("userconfig/token", views.TenantUserTokenConfigView.as_view(), name='tenant-userconfig-token'),
    # path("userconfig", views.TenantUserConfigView.as_view(), name='tenant-userconfig'),
    path("userconfig/editfield", views.TenantUserConfigFieldSelectListView.as_view(), name='tenant-userconfig-editfield'),
]
