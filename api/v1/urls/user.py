from api.v1.views import (
    user as views_user,
)
from django.urls import path

from .tenant import tenant_router

tenant_user_router = tenant_router.register(r'user', views_user.UserViewSet, basename='tenant-user', parents_query_lookups=['tenant'])

tenant_user_router.register(r'app',
                            views_user.UserAppViewSet,
                            basename='tenant-user-app',
                            parents_query_lookups=['tenant', 'user'])

urlpatterns = [
    path('user/token/', views_user.UserTokenView.as_view(), name='user-token'),
    path('user/info/', views_user.UserInfoView.as_view(), name='user-info'),
    path('user/bind_info/', views_user.UserBindInfoView.as_view(), name='user-bind-info'),
]
