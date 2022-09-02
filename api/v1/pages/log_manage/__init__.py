from arkid.core import routers
from arkid.core.translation import gettext_default as _

router = routers.FrontRouter(
    path='log_manage',
    name=_('日志管理'),
    icon='log',
)