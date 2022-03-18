from api.v1.views import (
    user as views_user,
)
from django.urls import path, re_path
from django.conf.urls import url, include

from .tenant import tenant_router

tenant_user_router = tenant_router.register(
    r'user',
    views_user.UserViewSet,
    basename='tenant-user',
    parents_query_lookups=['tenant'],
)

tenant_user_router.register(
    r'app',
    views_user.UserAppViewSet,
    basename='tenant-user-app',
    parents_query_lookups=['tenant', 'user'],
)

urlpatterns = [
    path('user/token/', views_user.UserTokenView.as_view(), name='user-token'),
    path('user/info/', views_user.UserInfoView.as_view(), name='user-info'),
    path(
        'user/bind_info/', views_user.UserBindInfoView.as_view(), name='user-bind-info'
    ),
    path(
        'user/update_password/',
        views_user.UpdatePasswordView.as_view(),
        name='user-update-password',
    ),
    path(
        'user/reset_password/',
        views_user.ResetPasswordView.as_view(),
        name='user-reset-password',
    ),
    path('user/logout/', views_user.UserLogoutView.as_view(), name='user-logout'),
    path('user/logoff/', views_user.UserLogoffView.as_view(), name='user-logoff'),
    path('user/token_expire/', views_user.UserTokenExpireView.as_view(),
         name='user-token-expire'),
    path(
        'user/manage_tenants/',
        views_user.UserManageTenantsView.as_view(),
        name='user-manage-tenants',
    ),
    url(
        r'^user/invitation/(?P<username>[\w]+)/',
        views_user.InviteUserCreateAPIView.as_view(),
        name='user-invite',
    ),
    re_path(
        r'^tenant/(?P<tenant_uuid>[\w-]+)/user_list/',
        views_user.UserListAPIView.as_view(),
        name='tenant-user-list',
    ),
    re_path(
        r'^tenant/(?P<tenant_uuid>[\w-]+)/user_app_data/',
        views_user.UserAppDataView.as_view(),
        name='tenant-user-list',
    ),
]
