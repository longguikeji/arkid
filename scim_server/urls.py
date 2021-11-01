#!/usr/bin/env python3

try:
    from django.urls import re_path
except ImportError:
    from django.conf.urls import url as re_path

from scim_server.mssql_provider.users_view import UsersView as MssqlUsersView
from scim_server.mssql_provider.groups_view import GroupsView as MssqlGroupsView
from scim_server.in_memory_provider.users_view import InMemoryUsersView
from scim_server.in_memory_provider.groups_view import InMemoryGroupsView

# app_name = 'scim'

urlpatterns = [
    # This endpoint is used soley for middleware url purposes.
    # re_path(r'^$', views.SCIMView.as_view(implemented=False), name='root'),
    # re_path(r'^.search$', views.SearchView.as_view(implemented=False), name='search'),
    # re_path(r'^Users/.search$', views.UserSearchView.as_view(), name='users-search'),
    re_path(
        r'^memory/Users(?:/(?P<uuid>[^/]+))?$',
        InMemoryUsersView.as_view(),
        name='memory_users',
    ),
    # re_path(r'^Groups/.search$', views.GroupSearchView.as_view(), name='groups-search'),
    re_path(
        r'^memory/Groups(?:/(?P<uuid>[^/]+))?$',
        InMemoryGroupsView.as_view(),
        name='memory_groups',
    ),
    # re_path(r'^Me$', views.SCIMView.as_view(implemented=False), name='me'),
    # re_path(
    #     r'^ServiceProviderConfig$',
    #     views.ServiceProviderConfigView.as_view(),
    #     name='service-provider-config',
    # ),
    # re_path(
    #     r'^ResourceTypes(?:/(?P<uuid>[^/]+))?$',
    #     views.ResourceTypesView.as_view(),
    #     name='resource-types',
    # ),
    # re_path(
    #     r'^Schemas(?:/(?P<uuid>[^/]+))?$', views.SchemasView.as_view(), name='schemas'
    # ),
    # re_path(r'^Bulk$', views.SCIMView.as_view(implemented=False), name='bulk'),
    re_path(
        r'^mssql/Users(?:/(?P<uuid>[^/]+))?$',
        MssqlUsersView.as_view(),
        name='mssql_users',
    ),
    re_path(
        r'^mssql/Groups(?:/(?P<uuid>[^/]+))?$',
        MssqlGroupsView.as_view(),
        name='mssql_groups',
    ),
]
