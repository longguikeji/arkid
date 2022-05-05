from arkid.core import routers
from arkid.core.translation import gettext_default as _
from . import log_config,manager_log,user_log

router = routers.FrontRouter(
    path='log_manage',
    name=_('日志管理'),
    children=[
        log_config.router,
        manager_log.router,
        user_log.router,
    ]
)