from ..extension_manage import extension_admin
from arkid.core import routers
from arkid.core.translation import gettext_default as _
from . import language_admin,tenant_admin, platform_config

router = routers.FrontRouter(
    path='platform_admin',
    name=_('平台管理'),
    icon='platform_admin',
    children=[
        language_admin.router,
        tenant_admin.router,
        platform_config.router,
    ]
)