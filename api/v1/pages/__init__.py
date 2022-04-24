from . import (
    user_manage,
    desktop,
    app_manage,
    approve_manage
)
from arkid.core import routers


routers.register_front_routers(
    [
        desktop.router,
        user_manage.router,
        app_manage.router,
        approve_manage.router
    ]
)
