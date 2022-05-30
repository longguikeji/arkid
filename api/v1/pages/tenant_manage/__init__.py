from arkid.core import routers
from arkid.core.translation import gettext_default as _
from . import center_arkid,child_manager,tenant_config,extension_manage,front_theme

router = routers.FrontRouter(
    path='tenant_manage',
    name=_('租户管理'),
    icon='tenant',
    children=[
        tenant_config.router,
        child_manager.router,
        front_theme.router,
        extension_manage.router,
        center_arkid.router
    ]
)