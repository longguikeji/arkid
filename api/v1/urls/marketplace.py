from api.v1.views import (
    marketplace as views_marketplace
)

from .tenant import tenant_router

tenant_marketplace_router = tenant_router.register(r'marketplace', views_marketplace.MarketPlaceViewSet, basename='tenant-marketplace', parents_query_lookups=['tenant'])
