from arkid.core import routers
from arkid.core.translation import gettext_default as _
from . import extension_admin,extension_manage,extension_psc

router = routers.FrontRouter(
    path='extension_manage',
    name=_('插件管理'),
    icon='extension',
    children=[
        extension_manage.router,
        extension_admin.router,
        extension_psc.router,
    ]
)