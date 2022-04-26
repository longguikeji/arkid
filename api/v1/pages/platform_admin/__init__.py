from arkid.core import routers
from arkid.core.translation import gettext_default as _
from . import extension_admin,language_admin,tenant_admin

router = routers.FrontRouter(
    path='platform_admin',
    name=_('平台管理'),
    children=[
        extension_admin.router,
        language_admin.router,
        tenant_admin.router
    ]
)