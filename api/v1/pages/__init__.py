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
    platform_admin,
    tenant_manage
)
from arkid.core import routers


routers.register_front_routers(
    [
        mine.router,
        desktop.router,
        app_manage.router,
        user_manage.router,
        auth_manage.router,
        permission_manage.router,
        approve_manage.router,
        data_source_manage.router,
        developer_manage.router,
        log_manage.router,
        charts_manage.router,
        tenant_manage.router,
        platform_admin.router,
    ]
)
