from django.urls import path
from api.v1.views import (
    marketplace as views_marketplace
)

from rest_framework_extensions.routers import ExtendedSimpleRouter
from django.urls import re_path
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'marketplace', views_marketplace.MarketPlaceViewSet, basename='marketplace')
