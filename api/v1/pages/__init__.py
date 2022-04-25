from . import (
    user_manage,
    desktop,
    app_manage,
    approve_manage,
    auth_manage,
    charts_manage,
    data_source_manage,
    developer_manage,
    log_manage,
    mine,
    permission_manage,
)
from arkid.core import routers


routers.register_front_routers(
    [
        desktop.router,
        user_manage.router,
        app_manage.router,
        approve_manage.router,
        auth_manage.router,
        charts_manage.router,
        data_source_manage.router,
        developer_manage.router,
        log_manage.router,
        mine.router,
        permission_manage.router
    ]
)
