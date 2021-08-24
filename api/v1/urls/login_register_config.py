from api.v1.views import (
    login_register_config as views_config,
)

from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(
    r'login_register_config',
    views_config.LoginRegisterConfigViewSet,
    basename='login_register_config',
)
