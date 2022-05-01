from arkid.core import routers
from arkid.core.translation import gettext_default as _
from . import center_arkid,child_manager,tenant_config,extension_manage

router = routers.FrontRouter(
    path='tenant_manage',
    name=_('租户管理'),
    children=[
        center_arkid.router,
        child_manager.router,
        tenant_config.router,
        extension_manage.router
    ]
)