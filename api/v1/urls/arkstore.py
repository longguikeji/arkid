# from api.v1.views import (
#     arkstore as views_arkstore,
# )

# from .tenant import tenant_router


# tenant_router.register(r'arkstore',
#         views_arkstore.MarketPlaceViewSet,
#         basename='tenant-arkstore',
#         parents_query_lookups=['tenant',])

# # urlpatterns = [
# #     path('tags/', views_arkstore.MarketPlaceTagsViewSet.as_view(), name='tags'),
# # ]

from django.urls import re_path

from api.v1.views import arkstore


urlpatterns = [
    re_path(
        r'^tenant/(?P<tenant_uuid>[\w-]+)/arkstore/',
        arkstore.ArkStoreAPIView.as_view(),
        name='arkstore',
    ),
]
