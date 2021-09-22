from api.v1.views import (
    other_auth_factor as views_config,
)

from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(
    r'other_auth_factor',
    views_config.OtherAuthFactorViewSet,
    basename='other_auth_factor',
)
