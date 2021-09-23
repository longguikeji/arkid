from api.v1.views import statistics

from .tenant import tenant_router


tenant_router.register(r'statistics',
        statistics.StatisticsView,
        basename='tenant-statistics',
        parents_query_lookups=['tenant',])
