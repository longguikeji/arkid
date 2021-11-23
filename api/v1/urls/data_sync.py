#!/usr/bin/env python3

from api.v1.views import data_sync as views_data_sync

from .tenant import tenant_router


tenant_data_sync_router = tenant_router.register(
    r'data_sync',
    views_data_sync.DataSyncViewSet,
    basename='tenant-data-sync',
    parents_query_lookups=['tenant'],
)
